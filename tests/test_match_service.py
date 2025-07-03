import unittest
from unittest.mock import patch, MagicMock
from backend.langgraph_engine.nodes.inferencer import match_services

class MatchServicesTest(unittest.TestCase):

    @patch("backend.langgraph_engine.nodes.inferencer.get_chat_client")
    @patch("backend.langgraph_engine.nodes.inferencer.get_inferencing_prompt")
    @patch("backend.langgraph_engine.nodes.inferencer.compute_confidence")
    def test_match_services_success(self, mock_confidence, mock_prompt, mock_get_llm):
        # Mock prompt
        mock_prompt.return_value = "Mock prompt for LLM"

        # Mock LLM response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = '''
        [
            {
                "from": "service-a",
                "to": "service-b",
                "type": "http",
                "via": "/pay"
            }
        ]
        '''
        mock_get_llm.return_value = mock_llm

        # Mock confidence score
        mock_confidence.return_value = 0.85

        # Prepare test state
        test_state = {
            "repos": {
                "service-a": ["file content"],
                "service-b": ["file content"]
            },
            "calls": [
                {
                    "source": "service-a",
                    "type": "http",
                    "target_guess": "service-b",
                    "via": "/pay"
                }
            ]
        }

        # Act
        result = match_services(test_state)

        # Assert
        self.assertIn("inferred", result)
        self.assertEqual(len(result["inferred"]), 1)
        inferred = result["inferred"][0]
        self.assertEqual(inferred["from"], "service-a")
        self.assertEqual(inferred["to"], "service-b")
        self.assertEqual(inferred["type"], "http")
        self.assertEqual(inferred["via"], "/pay")
        self.assertEqual(inferred["confidence"], 0.85)

if __name__ == "__main__":
    unittest.main()
