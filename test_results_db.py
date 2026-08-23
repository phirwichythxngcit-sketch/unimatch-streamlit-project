from results_db import delete_result, list_results, save_result


def test_save_list_and_delete_result(tmp_path):
    database = tmp_path / "results.db"
    first_id = save_result("คนแรก", "INTP", "วิทยาการคอมพิวเตอร์", 91, "งบน้อย", database)
    second_id = save_result("คนที่สอง", "INFJ", "จิตวิทยา", 82, "งบปานกลาง", database)

    records = list_results(database)
    assert [record["id"] for record in records] == [second_id, first_id]
    assert records[0]["participant_name"] == "คนที่สอง"
    assert records[0]["compatibility"] == 82

    assert delete_result(first_id, database)
    assert [record["id"] for record in list_results(database)] == [second_id]
    assert not delete_result(9999, database)


def test_result_name_and_compatibility_are_validated(tmp_path):
    database = tmp_path / "results.db"

    try:
        save_result("  ", "INTP", "คณะทดสอบ", 70, None, database)
        assert False, "expected empty name to fail"
    except ValueError:
        pass

    try:
        save_result("ทดสอบ", "INTP", "คณะทดสอบ", 101, None, database)
        assert False, "expected invalid compatibility to fail"
    except ValueError:
        pass
