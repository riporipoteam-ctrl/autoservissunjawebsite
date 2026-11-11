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


if __name__ == "__main__":
    unittest.main()
