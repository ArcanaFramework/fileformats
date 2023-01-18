from fileformats.serialization import Json, Yaml


SAMPLE_JSON = """{
    "a": "string field",
    "alist": [0, 1, 2, 3, 4, 5],
    "anesteddict": {
        "x": null,
        "y": [],
        "z": 42.0
    }
}"""

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


def test_json_to_yaml(work_dir):
    in_file = work_dir / "test.json"
    with open(in_file, "w") as f:
        f.write(SAMPLE_JSON)
    jsn = Json(in_file)
    jsn.validate()
    yml = Yaml.convert(jsn)
    yml.validate()
    assert yml.contents == SAMPLE_YAML


def test_yaml_to_json(work_dir):
    in_file = work_dir / "test.yaml"
    with open(in_file, "w") as f:
        f.write(SAMPLE_JSON)
    yml = Yaml(in_file)
    yml.validate()
    jsn = Json.convert(yml)
    jsn.validate()
    assert yml.contents == SAMPLE_JSON
