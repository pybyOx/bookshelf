from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book

User = get_user_model()


class BookAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='oksana', password='pass12345')
        self.stranger = User.objects.create_user(username='petya', password='pass123456')
        self.book = Book.objects.create(
            title='Clean Code',
            author='Robert Martin',
            year=2008,
            owner=self.owner,
        )
        self.list_url = reverse('book-list')
        self.detail_url = reverse('book-detail', args=[self.book.pk])

    # ── чтение ────────────────────────────────────────────────

    def test_anonymous_can_list_books(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Clean Code')

    def test_anyone_can_retrieve_book_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Clean Code')

    # ── создание ──────────────────────────────────────────────

    def test_anonymous_cannot_create_book(self):
        response = self.client.post(
            self.list_url,
            {'title': 'Title', 'author': 'Robert Martin', 'year': 2000},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 1)

    def test_authenticated_user_creates_book_with_himself_as_owner(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            {
                'title': 'Title',
                'author': 'Robert Martin',
                'year': 2000,
                'owner': self.stranger.pk,   # попытка записать книгу на чужое имя
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        new_book = Book.objects.get(title='Title')
        self.assertEqual(new_book.owner, self.owner)

    # ── изменение ─────────────────────────────────────────────

    def test_owner_can_update_own_book(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(self.detail_url, {'title': 'Новое'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Новое')

    def test_stranger_cannot_update_foreign_book(self):
        self.client.force_authenticate(user=self.stranger)

        response = self.client.patch(self.detail_url, {'title': 'Новое'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Clean Code')

    # ── удаление ──────────────────────────────────────────────

    def test_owner_can_delete_own_book(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_stranger_cannot_delete_foreign_book(self):
        self.client.force_authenticate(user=self.stranger)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_anonymous_cannot_delete_book(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
        