from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from django.core.mail import send_mail
from django.core.cache import cache
class Author(models.Model):
    author_user = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    def update_rating(self):
        post_rating = sum(post.rating for post in self.post_set.all()) * 3
        comment_rating = sum(comment.rating for comment in self.user.comment_set.all())
        post_comment_rating = sum(comment.rating for post in self.post_set.all() for comment in post.comment_set.all())
        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()


class Category(models.Model):
    category_name = models.CharField(max_length=128, unique=True)

class Post(models.Model):
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOISES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type_post = models.CharField(max_length=2, choices=CATEGORY_CHOISES, default=ARTICLE)
    time_create = models.DateTimeField(auto_now_add=True)
    post_category = models.ManyToManyField(Category, through='PostCategory')
    post_title = models.CharField(max_length=128)
    post_content = models.TextField()
    post_rating = models.IntegerField(default=0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return self.post_content[:123] + '...' if len(self.post_content) > 123 else self.post_content

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f"post-{self.pk}")

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    time_comment = models.DateTimeField(auto_now_add=True)
    rating_comment = models.IntegerField(default=0)

    def like(self):
        self.rating_comment += 1
        self.save()

    def dislike(self):
        self.rating_comment -= 1
        self.save()


class Subscriber(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    subscribed_categories = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    def __str__(self):
        return self.email
