import sys
import os
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "BorderP45")))

class TestBorderP45(unittest.TestCase):
    def setUp(self):
        from app import app
        self.client = app.test_client()

    def test_index_route(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'BorderP45 Portal', res.data)
        self.assertIn(b'TON Transfer', res.data)
        self.assertIn(b'Jetton Transfer', res.data)
        self.assertIn(b'tonconnect-ui.min.js', res.data)
        self.assertIn(b'id="ton-connect"', res.data)
        self.assertIn(b'TON_CONNECT_UI.TonConnectUI', res.data)

    def test_static_and_manifest_routes(self):
        res_sw = self.client.get('/sw.js')
        self.assertEqual(res_sw.status_code, 200)
        self.assertIn('javascript', res_sw.content_type)

        res_manifest = self.client.get('/manifest.json')
        self.assertEqual(res_manifest.status_code, 200)
        self.assertIn('json', res_manifest.content_type)

        res_tonconnect_manifest = self.client.get('/tonconnect-manifest.json')
        self.assertEqual(res_tonconnect_manifest.status_code, 200)
        self.assertIn('json', res_tonconnect_manifest.content_type)
        data = json.loads(res_tonconnect_manifest.data)
        self.assertEqual(data.get('name'), 'BorderP45 Portal')

    def test_transfer_routes(self):
        res_ton = self.client.post('/api/transfer/ton', json={
            'recipient': 'EQD123',
            'amount': '10.5',
            'comment': 'Test TON transfer'
        })
        self.assertEqual(res_ton.status_code, 200)
        data_ton = json.loads(res_ton.data)
        self.assertTrue(data_ton['success'])
        self.assertEqual(data_ton['recipient'], 'EQD123')

        res_jetton = self.client.post('/api/transfer/jetton', json={
            'jetton_master': 'EQB456',
            'recipient': 'EQD123',
            'amount': '100',
            'comment': 'Test Jetton transfer'
        })
        self.assertEqual(res_jetton.status_code, 200)
        data_jetton = json.loads(res_jetton.data)
        self.assertTrue(data_jetton['success'])
        self.assertEqual(data_jetton['jetton_master'], 'EQB456')

    def test_tonconnect_parse_and_connect_routes(self):
        test_endpoint_url = (
            "https://connect.gramwallet.io/?v=2&id=fd97f7f6ad60461e4885761d2cdc430d130c6c19854af1e8771685d0675e1f11"
            "&trace_id=01a0ca5f-f49a-73b4-b0e9-d5cfeed14928"
            "&r=%7B%22manifestUrl%22%3A%22https%3A%2F%2Ftonviewer.com%2Ftc-manifest.json%22%2C%22items%22%3A%5B%7B%22name%22%3A%22ton_addr%22%7D%2C%7B%22name%22%3A%22ton_proof%22%2C%22payload%22%3A%220d21184fedec258206e26530bd09fc347b1279f83b12e87ccbbeab6ab1286e12%22%7D%5D%7D"
            "&ret=https%3A%2F%2Ftonviewer.com%2Ftransaction%2Ff177ef98dad79d87295f17cd8e7816ab6ef715355a7e22c7477baf701b9017a6"
        )

        res_parse = self.client.post('/api/tonconnect/parse', json={'url': test_endpoint_url})
        self.assertEqual(res_parse.status_code, 200)
        data_parse = json.loads(res_parse.data)
        self.assertTrue(data_parse['success'])
        self.assertEqual(data_parse['parsed']['version'], '2')
        self.assertEqual(data_parse['parsed']['id'], 'fd97f7f6ad60461e4885761d2cdc430d130c6c19854af1e8771685d0675e1f11')
        self.assertEqual(data_parse['parsed']['trace_id'], '01a0ca5f-f49a-73b4-b0e9-d5cfeed14928')
        self.assertEqual(data_parse['parsed']['manifest_url'], 'https://tonviewer.com/tc-manifest.json')
        self.assertEqual(len(data_parse['parsed']['items']), 2)
        self.assertEqual(data_parse['parsed']['items'][0]['name'], 'ton_addr')
        self.assertEqual(data_parse['parsed']['items'][1]['name'], 'ton_proof')

        res_parse_get = self.client.get(f'/api/tonconnect/parse?url={test_endpoint_url}')
        self.assertEqual(res_parse_get.status_code, 200)
        data_parse_get = json.loads(res_parse_get.data)
        self.assertTrue(data_parse_get['success'])

        view_url = "https://go.gramwallet.io/view/?ton=UQBVHkPhkJvxjq2bDun3-ju0cQNOpHYxVkWCwYAyClohC9Bn"
        res_view = self.client.post('/api/tonconnect/parse', json={'url': view_url})
        self.assertEqual(res_view.status_code, 200)
        data_view = json.loads(res_view.data)
        self.assertTrue(data_view['success'])
        self.assertEqual(data_view['parsed']['ton_address'], 'UQBVHkPhkJvxjq2bDun3-ju0cQNOpHYxVkWCwYAyClohC9Bn')

        res_connect = self.client.post('/api/tonconnect/connect', json={
            'id': 'fd97f7f6ad60461e4885761d2cdc430d130c6c19854af1e8771685d0675e1f11',
            'manifest_url': 'https://tonviewer.com/tc-manifest.json'
        })
        self.assertEqual(res_connect.status_code, 200)
        data_connect = json.loads(res_connect.data)
        self.assertTrue(data_connect['success'])
        self.assertEqual(data_connect['client_id'], 'fd97f7f6ad60461e4885761d2cdc430d130c6c19854af1e8771685d0675e1f11')
        self.assertIn('session_id', data_connect)

if __name__ == '__main__':
    unittest.main()
