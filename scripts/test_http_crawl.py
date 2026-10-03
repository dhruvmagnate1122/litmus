"""Fixture-only HTTP observations; never accepts a deployed URL."""
import http.client
import json
import threading
import unittest
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.robotparser import RobotFileParser

from check import derive, load_packs, validate_evidence

FIXTURE = Path(__file__).parent / "fixtures/http-crawl.json"


class Markup(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.noindex = False
        self.canonicals = []
        self.links = []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("name", "").lower() == "robots":
            self.noindex |= "noindex" in a.get("content", "").lower().split(",")
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonicals.append(a.get("href", ""))
        if tag == "a":
            self.links.append(a.get("href", ""))


class HttpCrawlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text())
        routes = cls.fixture["routes"]

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                route = routes.get(self.path, {"status": 404})
                self.send_response_only(route["status"])
                for key, value in route.get("headers", {}).items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(route.get("body", "").encode())

            def log_message(self, *args):
                pass

        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.rules = {r["id"]: r for r in load_packs(FIXTURE.parents[2])["seo"]["checks"]}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def fetch(self, path):
        # Direct loopback connection: no proxy, DNS, or automatic redirects.
        self.assertTrue(path.startswith("/") and not path.startswith("//"))
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read().decode()
        finally:
            conn.close()

    def follow(self, path):
        chain = []
        for _ in range(5):
            status, headers, body = self.fetch(path)
            chain.append([path, status])
            if status not in {301, 302, 303, 307, 308}:
                return status, body, chain
            path = headers["Location"]
        return None, "", chain

    def observe(self, case):
        path, check = case["path"], case["check"]
        status, headers, body = self.fetch(path)
        markup = Markup(body)
        details = {"path": path, "status": status}
        if check == "SEO-STATUS":
            final, _, chain = self.follow(path)
            passed = final == 200
            details["chain"] = chain
        elif check == "SEO-INDEX":
            passed = status == 200 and not markup.noindex and "noindex" not in headers.get("X-Robots-Tag", "").lower()
            details["meta_noindex"] = markup.noindex
            details["x_robots_tag"] = headers.get("X-Robots-Tag")
        elif check == "SEO-ROBOTS":
            robots_status, _, robots_body = self.fetch("/robots.txt")
            robots = RobotFileParser()
            robots.parse(robots_body.splitlines())
            passed = robots_status == 200 and robots.can_fetch("*", path)
            details["robots"] = robots_body
        elif check == "SEO-CANONICAL":
            targets = [[p, self.fetch(p)[0]] for p in markup.canonicals]
            passed = targets == [["/ok", 200]]
            details["targets"] = targets
        elif check == "SEO-BROKEN":
            targets = [[p, self.follow(p)[0]] for p in markup.links]
            passed = bool(targets) and all(s == 200 for _, s in targets)
            details["targets"] = targets
        else:
            self.fail("Unmapped fixture check: " + check)
        return {
            "type": "runtime", "result": "PASS" if passed else "FAIL",
            "details": json.dumps(details, sort_keys=True),
            "observed_at": "2026-09-30T12:00:00Z",
            "environment": "synthetic-loopback-fixture",
            "producer": {"kind": "tool", "name": "scripts/test_http_crawl.py"},
            "reference": "scripts/fixtures/http-crawl.json#/cases/" + str(self.fixture["cases"].index(case)),
        }

    def test_cases_and_evidence_contract(self):
        for case in self.fixture["cases"]:
            with self.subTest(case=case["id"]):
                record = self.observe(case)
                self.assertEqual(record["result"], case["expected"])
                validate_evidence({case["check"]: [record]})
                rule = self.rules[case["check"]]
                expected = "UNKNOWN" if case["check"] == "SEO-INDEX" and case["expected"] == "PASS" else case["expected"]
                self.assertEqual(derive(rule, [record])[0], expected)
                # Repeated HTTP observations yield identical evidence references/details.
                self.assertEqual(record, self.observe(case))

    def test_redirect_chain_is_preserved(self):
        self.assertEqual(self.follow("/old")[2], [["/old", 301], ["/moved", 302], ["/ok", 200]])
        self.assertEqual(len(self.follow("/loop")[2]), 5)

    def test_missing_partial_and_review_evidence(self):
        rule = self.rules["SEO-INDEX"]
        case = next(c for c in self.fixture["cases"] if c["id"] == "indexable")
        runtime = self.observe(case)
        self.assertEqual(derive(rule, [])[0], "UNKNOWN")
        self.assertEqual(derive(rule, [runtime], True)[0], "REVIEW")
        source = dict(runtime, type="source", producer={"kind": "manual", "name": "fixture intent review"},
                      details="Fixture /ok is intended public/indexable; synthetic source attestation.")
        validate_evidence({"SEO-INDEX": [source, runtime]})
        self.assertEqual(derive(rule, [source, runtime], True)[0], "PASS")
        review = dict(runtime, result="REVIEW", details="Index intent unresolved")
        self.assertEqual(derive(rule, [source, runtime, review])[0], "REVIEW")
        failure = self.observe(next(c for c in self.fixture["cases"] if c["id"] == "meta-noindex"))
        self.assertEqual(derive(rule, [source, runtime, failure])[0], "FAIL")
        self.assertEqual(derive(self.rules["SEO-RENDER"], [])[0], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
