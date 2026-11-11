import unittest
from unittest.mock import patch

from tools import refresh_photos as rp


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class SocialPhotoTests(unittest.TestCase):
    @patch("requests.get")
    def test_tikwm_photo_carousel_keeps_every_image(self, mock_get):
        mock_get.return_value = FakeResponse({
            "data": {
                "videos": [{
                    "video_id": "7700000000000000000",
                    "create_time": 1794326400,
                    "images": [
                        "https://example.invalid/one.jpg",
                        "https://example.invalid/two.jpg",
                        "https://example.invalid/three.jpg",
                    ],
                    "title": "Peugeot servis",
                }]
            }
        })

        posts = rp.from_tikwm()

        self.assertEqual(3, len(posts))
        self.assertEqual([0, 1, 2], [p["media_index"] for p in posts])
        self.assertEqual(
            [
                "tiktok:7700000000000000000:0",
                "tiktok:7700000000000000000:1",
                "tiktok:7700000000000000000:2",
            ],
            [p["media_id"] for p in posts],
        )
        self.assertTrue(all(p["post_id"] == "7700000000000000000" for p in posts))
        self.assertTrue(all(p["source"] == "tiktok" for p in posts))

    def test_source_detection_supports_all_linked_socials(self):
        self.assertEqual("tiktok", rp.source_of({"href": "https://www.tiktok.com/@autoservissunja/photo/123"}))
        self.assertEqual("instagram", rp.source_of({"href": "https://www.instagram.com/p/ABC123/"}))
        self.assertEqual("facebook", rp.source_of({"href": "https://www.facebook.com/story.php?story_fbid=123&id=456"}))

    def test_instagram_post_id_is_shortcode(self):
        self.assertEqual(
            "ABC123xyz",
            rp.post_id_of({"source": "instagram", "href": "https://www.instagram.com/p/ABC123xyz/"}),
        )

    @patch.object(rp, "_gallery_dl")
    def test_gallery_dl_fallback_expands_tiktok_photo_carousel(self, mock_gallery):
        mock_gallery.return_value = [
            ("https://example.invalid/slide-1.jpg", {"extension": "jpg", "post_type": "image"}),
            ("https://example.invalid/audio.m4a", {"extension": "m4a", "post_type": "audio"}),
            ("https://example.invalid/slide-2.webp", {"extension": "webp", "post_type": "image"}),
        ]

        posts = rp.expand_tiktok_photo(
            "7700000000000000001",
            "https://www.tiktok.com/@autoservissunja/photo/7700000000000000001",
            1794326400,
            "Rad u radionici",
        )

        self.assertEqual(2, len(posts))
        self.assertEqual([0, 1], [p["media_index"] for p in posts])
        self.assertEqual(
            [
                "tiktok:7700000000000000001:0",
                "tiktok:7700000000000000001:1",
            ],
            [p["media_id"] for p in posts],
        )

    def test_gallery_dl_json_parser_accepts_nested_output(self):
        raw = '[[2, "", {"category": "tiktok"}], [3, "https://cdn.invalid/a.jpg", {"extension": "jpg"}]]'
        rows = rp._gallery_dl_url_rows(raw)
        self.assertEqual(
            [("https://cdn.invalid/a.jpg", {"extension": "jpg"})],
            rows,
        )


    @patch.object(rp, "_gallery_dl")
    def test_direct_tiktok_photo_is_marked_as_original_quality(self, mock_gallery):
        mock_gallery.return_value = [
            ("https://cdn.invalid/full.jpg", {"extension": "jpg", "post_type": "image"}),
        ]
        posts = rp.expand_tiktok_photo(
            "7700000000000000002",
            "https://www.tiktok.com/@autoservissunja/photo/7700000000000000002",
            1794326400,
            "Servis",
        )
        self.assertEqual("original", posts[0]["quality_source"])

    def test_known_media_without_quality_v_needs_upgrade(self):
        pools = {
            "gallery": [{"media_id": "tiktok:123:0", "quality_v": 1}],
            "hero": [{"media_id": "tiktok:123:0"}],
            "heroMobile": [{"media_id": "tiktok:123:0", "quality_v": 2}],
        }
        self.assertTrue(rp.needs_quality_upgrade(pools, "tiktok:123:0"))
        for pool in pools.values():
            for entry in pool:
                entry["quality_v"] = 2
        self.assertFalse(rp.needs_quality_upgrade(pools, "tiktok:123:0"))


    def test_rebuild_display_pools_uses_gallery_quality_v2_sources(self):
        pools = {
            "gallery": [
                {
                    "src": "assets/photos/tt-20261110-abcd.webp",
                    "media_id": "tiktok:1:0",
                    "quality_v": 2,
                    "date": "2026-11-10",
                    "href": "https://www.tiktok.com/@autoservissunja/photo/1",
                    "title": "A",
                    "source": "tiktok",
                    "post_id": "1",
                    "media_index": 0,
                },
                {
                    "src": "assets/photos/tt-old.webp",
                    "media_id": "tiktok:2:0",
                    "quality_v": 0,
                    "date": "2026-11-08",
                },
            ]
        }

        rebuilt = rp.rebuild_display_pools(pools)

        self.assertEqual(1, len(rebuilt["heroMobile"]))
        self.assertEqual(
            "assets/photos/tt-20261110-abcd.webp",
            rebuilt["heroMobile"][0]["src"],
        )
        self.assertEqual(
            "assets/photos/tt-wide-20261110-abcd.webp",
            rebuilt["hero"][0]["src"],
        )
        self.assertEqual(2, rebuilt["hero"][0]["quality_v"])


if __name__ == "__main__":
    unittest.main()
