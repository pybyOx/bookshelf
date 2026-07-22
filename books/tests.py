from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

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
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Clean Code')

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

        # 401, а не 403: аноним не предъявил учётных данных — провал аутентификации
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
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

        # 401 — аутентификации не было; 403 получает опознанный, но чужой юзер
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    # ── аутентификация по токену ──────────────────────────────────────────────

    def test_user_with_token_can_create_book(self):
        token = Token.objects.create(user=self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.post(
            self.list_url,
            {
                'title': 'Title',
                'author': 'Robert Martin',
                'year': 2000,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        new_book = Book.objects.get(title='Title')
        self.assertEqual(new_book.owner, self.owner)

    def test_invalid_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token abrakadabra123')

        response = self.client.post(
            self.list_url,
            {
                'title': 'Title',
                'author': 'Robert Martin',
                'year': 2000,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 1)

    # ── пагинация ────────────────────────────────────────────────

    def test_list_is_paginated(self):
        for n in range(2):
            Book.objects.create(
                title=f'Title {n}',
                author='Robert Martin',
                year=2000,
                owner=self.owner
            )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_second_page_is_last(self):
        for n in range(2):
            Book.objects.create(
                title=f'Title {n}',
                author='Robert Martin',
                year=2000,
                owner=self.owner,
            )

        response = self.client.get(self.list_url, {'page': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 1)   # 3 книги при PAGE_SIZE=2
        self.assertIsNone(response.data['next'])             # дальше страниц нет
        self.assertIsNotNone(response.data['previous'])

    def test_page_out_of_range_returns_404(self):
        response = self.client.get(self.list_url, {'page': 99})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
