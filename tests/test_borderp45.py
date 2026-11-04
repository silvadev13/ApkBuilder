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
        self.assertIn(b'tabindex="0"', res.data)
        self.assertIn(b'tabindex="-1"', res.data)
        self.assertIn(b'ArrowRight', res.data)

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

    def test_ton_api_endpoints(self):
        test_addr = 'EQD000000000000000000000000000000000000000000000'

        # Test account endpoint
        res_acc = self.client.get(f'/api/ton/account/{test_addr}')
        self.assertEqual(res_acc.status_code, 200)
        data_acc = json.loads(res_acc.data)
        self.assertTrue(data_acc['success'])
        self.assertEqual(data_acc['address'], test_addr)
        self.assertIn('balance', data_acc)

        # Test transactions endpoint
        res_tx = self.client.get(f'/api/ton/transactions/{test_addr}')
        self.assertEqual(res_tx.status_code, 200)
        data_tx = json.loads(res_tx.data)
        self.assertTrue(data_tx['success'])
        self.assertEqual(data_tx['address'], test_addr)
        self.assertIsInstance(data_tx['transactions'], list)

if __name__ == '__main__':
    unittest.main()
