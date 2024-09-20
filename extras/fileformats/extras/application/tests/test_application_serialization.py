# import sys
# import pytest
from fileformats.application import Json, Yaml


SAMPLE_JSON = (
    """{"a": "string field", "alist": [0, 1, 2, 3, 4, 5], """
    """"anesteddict": {"x": null, "y": [], "z": 42.0}}"""
)

SAMPLE_YAML = """a: string field
alist:
- 0
- 1
- 2
- 3
- 4
- 5
anesteddict:
  x: null
  y: []
  z: 42.0
"""


# @pytest.mark.xfail(
#     sys.version_info.minor <= 9,
#     reason="upstream Pydra issue with type-checking 'type' objects",
# )
def test_json_to_yaml(work_dir):
    in_file = work_dir / "test.json"
    with open(in_file, "w") as f:
        f.write(SAMPLE_JSON)
    jsn = Json(in_file)
    yml = Yaml.convert(jsn)
    assert yml.raw_contents == SAMPLE_YAML


# @pytest.mark.xfail(
#     sys.version_info.minor <= 9,
#     reason="upstream Pydra issue with type-checking 'type' objects",
# )
def test_yaml_to_json(work_dir):
    in_file = work_dir / "test.yaml"
    with open(in_file, "w") as f:
        f.write(SAMPLE_JSON)
    yml = Yaml(in_file)
    jsn = Json.convert(yml)
    assert jsn.raw_contents == SAMPLE_JSON
