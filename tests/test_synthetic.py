from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream


def test_synthetic_generator_schema_and_size():
    df = SyntheticWebVitalsStream(seed=1).generate(250)
    assert len(df) == 250
    for col in ["lcp_ms", "fid_ms", "cls", "edge_cache_enabled", "network_rtt_ms"]:
        assert col in df.columns
    assert df["edge_cache_enabled"].between(0, 1).all()
