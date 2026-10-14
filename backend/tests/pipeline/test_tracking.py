from pipeline.tracking import calculate_image_hash


def test_hash_tracks_content_not_filename(tmp_path):
    first = tmp_path / 'first.jpg'
    second = tmp_path / 'second.jpg'
    first.write_bytes(b'image')
    second.write_bytes(b'image')
    assert calculate_image_hash(first) == calculate_image_hash(second)
    second.write_bytes(b'changed')
    assert calculate_image_hash(first) != calculate_image_hash(second)
