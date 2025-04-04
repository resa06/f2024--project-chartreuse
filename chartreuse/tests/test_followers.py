from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from urllib.parse import quote
from chartreuse.views import Host
from chartreuse.models import User, Node
import base64

class FollowersTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Host.host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

        cls.host = Host.host

        cls.client = APIClient()

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': cls.host,
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'http://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'host': cls.host,
            'firstName': 'John',
            'lastName': 'Smith',
        }

        cls.node = Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='abc',password='123',follow_status='INCOMING',status='ENABLED')
        cls.creds = {'Authorization' : 'Basic ' + base64.b64encode(b'abc:123').decode('utf-8')}
        # Create test users
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json', headers=cls.creds)
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json', headers=cls.creds)

        # log in as user 1
        cls.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        cls.user_id = quote(f"{cls.test_user_1_data['host']}chartreuse/api/authors/1", safe='')
        cls.follower_id = quote(f"{cls.test_user_2_data['host']}chartreuse/api/authors/2", safe='')


        # add user 2 as a follower of user 1 (user 1 accepted the request)
        cls.response = cls.client.post(reverse('chartreuse:add_follower', args=[cls.user_id, cls.follower_id]), headers=cls.creds)

    def setUp(self):
        '''
        Log in as user 1 again because setUpClass does not carry login information
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        # self.response = self.client.post(reverse('chartreuse:add_follower', args=[self.user_id, self.follower_id]), headers=self.creds)
        
    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()
    
    """
    
    def test_follow_user(self):
        '''
        This tests adding a follower.
        '''
        # self.response = self.client.post(reverse('chartreuse:add_follower', args=[self.user_id, self.follower_id]), headers=self.creds)
        # Check if follower added successfully
        
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(self.response.json()['message'], 'Follower added')
    
    def test_unfollow_user(self):
        '''
        This tests removing a follower.
        '''
        # Now remove user2 as a follower
        response = self.client.delete(reverse('chartreuse:remove_follower', args=[self.user_id, self.follower_id]), headers=self.creds)

        # Check if follower removed successfully
        self.assertEqual(response.status_code, 204)

    def test_get_followers(self):
        '''
        This tests getting followers for a user.
        '''
        # Get the list of followers for Greg (user 1)
        response = self.client.get(reverse('chartreuse:get_followers', args=[self.user_id]), headers=self.creds)

        # Successfully got followers
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['followers'], list)
        self.assertEqual(len(response.json()['followers']), 1)  # Greg is followed by John
    
    def test_is_follower(self):
        '''
        This tests checking if a user is a follower.
        '''
        # Check if John is following Greg
        response = self.client.get(reverse('chartreuse:is_follower', args=[self.user_id, self.follower_id]), headers=self.creds)  # Greg is author, John is foreign_author

        # Successfully verified follower status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Is a follower')

    """