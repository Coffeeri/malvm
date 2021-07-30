"""This module contains tests for helper methods."""
import json

import malvm.controller.virtual_machine.hypervisor.virtualbox.vagrant as vagrant_helper


test_vagrantfile_json = {
    "fkieVM": "~/.local/share/malvm/vagrantfiles/fkieVM/Vagrantfile",
    "abcVM": "~/.local/share/malvm/vagrantfiles/abcVM/Vagrantfile"}


def test_remove_key_from_json_file(tmp_path):
    with (tmp_path / "testfile.json").open(mode="w") as opened_file:
        json.dump(test_vagrantfile_json, opened_file)
    vagrant_helper.remove_key_from_json_file("fkieVM", tmp_path / "testfile.json")

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

    monkeypatch.setattr(vagrant_helper, "get_vagrant_files_json_path", json_path)
    vagrant_helper.remove_vm_from_vagrant_files("abcVM")

    with json_path().open() as opened_file:
        actual_test_dict = json.load(opened_file)

    expected_test_dict = {
        "fkieVM": "~/.local/share/malvm/vagrantfiles/fkieVM/Vagrantfile"}

    assert type(actual_test_dict) == dict
    assert expected_test_dict == actual_test_dict
