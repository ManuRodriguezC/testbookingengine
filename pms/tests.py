from django.test import TestCase
from django.urls import reverse
from .models import Room, Room_type
from django.test import override_settings

# Override static files storage to prevent errors during test rendering
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class RoomsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up a room type and create multiple rooms for testing
        cls.room_type = Room_type.objects.create(
            name="Suite",
            price=200,
            max_guests=3
        )
        # Create 16 rooms: Room 0.0 to Room 3.3
        for i in range(4):
            for j in range(4):
                Room.objects.create(name=f"Room {i}.{j}", room_type=cls.room_type)

    def test_filter_successful_room_1(self):
        """
        Ensure the filtering by room name works correctly.
        Expect 4 rooms containing 'Room 3' in the name.
        """
        filter_room_name = 'Room 3'
        rooms = Room.objects.filter(name__icontains=filter_room_name)
        self.assertEqual(len(rooms), 4)

    def test_list_view_status_ok(self):
        """
        Ensure the room list view returns HTTP 200 and uses the correct template.
        """
        response = self.client.get(reverse("rooms"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rooms.html")

    def test_room_filtering(self):
        """
        Ensure only filtered rooms are returned when a name query is provided.
        """
        Room.objects.create(name="Penthouse", room_type=self.room_type)
        response = self.client.get(reverse("rooms") + "?filter-rooms=penthouse")
        self.assertContains(response, "Penthouse")
        self.assertNotContains(response, "Room 0")

    def test_room_pagination(self):
        """
        Ensure only the first 10 rooms are displayed per page.
        """
        response = self.client.get(reverse("rooms"))
        self.assertEqual(len(response.context["rooms"]), 10)
        self.assertContains(response, "Room 0")

    def test_room_pagination_second_page(self):
        """
        Ensure the second page displays the remaining rooms.
        """
        response = self.client.get(reverse("rooms") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context["rooms"]), 5)

    def test_invalid_page_redirects_to_first(self):
        """
        Ensure an invalid page number redirects to the first page.
        """
        response = self.client.get(reverse("rooms") + "?page=999")
        self.assertRedirects(response, "/rooms/?page=1")
