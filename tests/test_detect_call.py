import unittest
from unittest.mock import patch, MagicMock

from backend.langgraph_engine.nodes.call_detector import detect_calls

class DetectCallsTest(unittest.TestCase):

    @patch("backend.langgraph_engine.nodes.call_detector.get_chat_client")
    def test_detect_calls_success(self, mock_get_chat_client):
        # Arrange: Mock LLM client and response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = '''
        [
            {
                "type": "http",
                "target": "payment-service",
                "details": "requests.post('/pay')"
            }
        ]
        '''
        mock_get_chat_client.return_value = mock_llm

        # Sample input state with dummy code
        test_state = {
            "repos": {
                "service-a": [
                    "import requests",
                    "requests.post('http://payment-service/pay')"
                ]
            }
        }

        # Act
        result_state = detect_calls(test_state)

        # Assert
        self.assertIn("calls", result_state)
        self.assertEqual(len(result_state["calls"]), 1)
        self.assertEqual(result_state["calls"][0]["source"], "service-a")
        self.assertEqual(result_state["calls"][0]["type"], "http")
        self.assertEqual(result_state["calls"][0]["target_guess"], "http://payment-service")
        self.assertIn("via", result_state["calls"][0])

if __name__ == "__main__":
    unittest.main()
