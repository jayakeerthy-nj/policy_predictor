from app.services.policy_parser_service import PolicyParserService


def test_rule_parser_extracts_direction_and_intensity():
    service = PolicyParserService()
    out = service.parse("Government announces aggressive increase in fuel import tariffs.")
    assert out.direction == "increase"
    assert out.intensity in {"medium", "high"}
    assert len(out.sectors) >= 1

