# Dried tea 2009-10: the first grading job stopped on a test-fixture error (no value read)

FIX-MARKER: dried-tea-2009-0.1.0-test-fix

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0. Dated 2026-11-09.

The sealed job `dried-tea-grade-v1` (2026-11-09, 15:10-15:13 UTC) synced the published grader and
its tests, then stopped at the unit tests: 2 of 11 failed. The grading step never ran, wrote no
output, and **no concentration value from CFIA's file was read**.

**What was wrong:** the tests, not the grader. The synthetic fixture gives mercury a value of 0 in one
of its three teas and the test asserted that V4 holds. But the
[pre-registration](dried-tea-2009-0.1.0-prereg.md) defines V4 as "every metal except beryllium is
above zero in all of the file's samples" and states that if V6 holds (mercury detected in fewer than
87% of samples), "V4 fails for mercury". The grader does exactly that. The test expected the wrong
thing, twice (`test_basic` and `test_v4_fails_on_a_zero_metal`).

**What changed:** only `test_dried_tea_grade.py` (fixture fix 0.1.1). Both assertions now expect
mercury in V4's failure list, and a new test checks that a zero lead value alone fails V4 when
mercury is detected everywhere. `dried_tea_grade.py` 0.1.0, the census note and every rule are
unchanged.

**Next:** job `dried-tea-grade-v2` waits until this note and the fixed test are public, syncs the
published code and grades V1, V2, V4-V6 and P1-P3 on the same file (same MD5) as registered.

MV2, Munim, Inc., mv2@munimtech.com
