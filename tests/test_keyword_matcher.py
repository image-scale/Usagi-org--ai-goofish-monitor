"""Tests for keyword rule matching engine."""
from src.keyword_matcher import build_search_text, evaluate_keyword_rules


def _sample_product_record():
    return {
        "商品信息": {
            "商品标题": "Sony A7M4 Full Frame Camera",
            "当前售价": "10000",
            "商品标签": ["verified", "free shipping"],
        },
        "卖家信息": {
            "卖家昵称": "Camera Store",
            "卖家个性签名": "Same-day delivery available",
        },
    }


def test_build_search_text_extracts_product_and_seller_fields():
    text = build_search_text(_sample_product_record())
    assert "sony a7m4" in text
    assert "camera store" in text
    assert "same-day delivery" in text


def test_evaluate_keyword_rules_or_match_any_keyword():
    text = build_search_text(_sample_product_record())
    result = evaluate_keyword_rules(["a7m4", "canon"], text)
    assert result["is_recommended"] is True
    assert result["analysis_source"] == "keyword"
    assert result["keyword_hit_count"] == 1
    assert result["matched_keywords"] == ["a7m4"]


def test_evaluate_keyword_rules_counts_multiple_hits():
    text = build_search_text(_sample_product_record())
    result = evaluate_keyword_rules(["a7m4", "verified", "camera store"], text)
    assert result["is_recommended"] is True
    assert result["keyword_hit_count"] == 3


def test_keyword_rules_case_insensitive():
    text = build_search_text(_sample_product_record())
    result = evaluate_keyword_rules(["SONY", "A7M4"], text)
    assert result["is_recommended"] is True
    assert result["keyword_hit_count"] == 2


def test_keyword_rules_no_match():
    text = build_search_text(_sample_product_record())
    result = evaluate_keyword_rules(["canon", "dslr"], text)
    assert result["is_recommended"] is False
    assert result["keyword_hit_count"] == 0


def test_alphanumeric_keyword_does_not_partial_match():
    result = evaluate_keyword_rules(["q1"], "fuji q1r5 flagship camera")
    assert result["is_recommended"] is False
    assert result["keyword_hit_count"] == 0


def test_alphanumeric_keyword_matches_full_token():
    result = evaluate_keyword_rules(["q1r5"], "fuji q1r5 flagship camera")
    assert result["is_recommended"] is True
    assert result["keyword_hit_count"] == 1


def test_keyword_rules_empty_keywords():
    result = evaluate_keyword_rules([], "some product text")
    assert result["is_recommended"] is False
    assert "No keyword rules" in result["reason"]


def test_keyword_rules_empty_search_text():
    result = evaluate_keyword_rules(["sony"], "")
    assert result["is_recommended"] is False
    assert "empty" in result["reason"].lower()
