"""This module contains tests for helper methods."""
import json

from malvm.utils import helper_methods

from malvm.utils.helper_methods import remove_key_from_json_file, \
    remove_vm_from_vagrant_files

test_vagrantfile_json = {
    "fkieVM": "~/.local/share/malvm/vagrantfiles/fkieVM/Vagrantfile",
    "abcVM": "~/.local/share/malvm/vagrantfiles/abcVM/Vagrantfile"}


def test_remove_key_from_json_file(tmp_path):
    with (tmp_path / "testfile.json").open(mode="w") as opened_file:
        json.dump(test_vagrantfile_json, opened_file)
    remove_key_from_json_file("fkieVM", tmp_path / "testfile.json")

    with (tmp_path / "testfile.json").open() as opened_file:
        actual_test_dict = json.load(opened_file)

    expected_test_dict = {
        "abcVM": "~/.local/share/malvm/vagrantfiles/abcVM/Vagrantfile"}

    assert type(actual_test_dict) == dict
    assert expected_test_dict == actual_test_dict


def test_remove_vm_from_vagrant_files(monkeypatch, tmp_path):
    def json_path():
        return tmp_path / "testfile.json"

    with json_path().open(mode="w") as opened_file:
        json.dump(test_vagrantfile_json, opened_file)

    monkeypatch.setattr(helper_methods, "get_vagrant_files_json_path", json_path)
    remove_vm_from_vagrant_files("abcVM")

    with json_path().open() as opened_file:
        actual_test_dict = json.load(opened_file)

    expected_test_dict = {
        "fkieVM": "~/.local/share/malvm/vagrantfiles/fkieVM/Vagrantfile"}

    assert type(actual_test_dict) == dict
    assert expected_test_dict == actual_test_dict
