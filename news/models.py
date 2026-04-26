from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db import models
from PIL import Image
import io


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("user_type", 2)  # default member
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", 1)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USER_TYPES = (
        (1, "admin"),
        (2, "member"),
    )
    user_type = models.IntegerField(choices=USER_TYPES, default=2)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self):
        return self.email

# ================= LOCATION =================
class Location(models.Model):
    name_en = models.CharField(max_length=50, default="Unknown")
    name_bn = models.CharField(max_length=50, default="অজানা")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en)
            slug = base_slug
            counter = 1

            while Location.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name_en

# ================= CATEGORY =================
class Category(models.Model):
    name_en = models.CharField(max_length=150, default="Category")
    name_bn = models.CharField(max_length=150, default="ক্যাটাগরি")
    slug = models.SlugField(unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name_en
    

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# ================= POLL =================

class Poll(models.Model):
    question_en = models.CharField(max_length=255)
    question_bn = models.CharField(max_length=255)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_en


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")

    option_en = models.CharField(max_length=150)
    option_bn = models.CharField(max_length=150)

    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.option_en


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("poll", "ip_address")


# ================= COMMENT =================

class Comment(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    name = models.CharField(max_length=100)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Tag(models.Model):
    name_bn = models.CharField(max_length=50, null=True)
    name_en = models.CharField(max_length=50, null=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en) if self.name_en else "tag"
            slug = base_slug
            counter = 1

            # Ensure uniqueness
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en or self.name_bn or "Tag"


class News(models.Model):
    polls = GenericRelation(Poll)
    comments = GenericRelation(Comment)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="news")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="news")
    title_en = models.CharField(max_length=150, default="News Title")
    title_bn = models.CharField(max_length=150, default="খবরের শিরোনাম")
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    image = models.ImageField(upload_to="news/")
    is_breaking = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    description_en = models.TextField(null=True, blank=True)
    description_bn = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def compress_to_webp(self, uploaded_image):
        img = Image.open(uploaded_image).convert("RGB")
        output = io.BytesIO()
        quality = 85  # start quality
        # reduce until ≤ 30KB
        while True:
            output.seek(0)
            img.save(output, format="WEBP", quality=quality, optimize=True)
            size_kb = output.tell() / 1024
            if size_kb <= 30 or quality <= 10:
                break
            quality -= 5
        output.seek(0)
        return output

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_en)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.image and hasattr(self.image, "file"):
            img_io = self.compress_to_webp(self.image)
            new_name = f"{slugify(self.title_en)}.webp"
            self.image.save(new_name, ContentFile(img_io.read()), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_en
    
class TrandingNews(models.Model):
    polls = GenericRelation(Poll)
    comments = GenericRelation(Comment)
    title_en = models.CharField(max_length=150, null=True)
    title_bn = models.CharField(max_length=150, null=True)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    image = models.ImageField(upload_to="news/")
    description_en = models.TextField(null=True, blank=True)
    description_bn = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def compress_to_webp(self, uploaded_image):
        img = Image.open(uploaded_image).convert("RGB")
        output = io.BytesIO()
        quality = 85  # start quality
        # reduce until ≤ 30KB
        while True:
            output.seek(0)
            img.save(output, format="WEBP", quality=quality, optimize=True)
            size_kb = output.tell() / 1024
            if size_kb <= 30 or quality <= 10:
                break
            quality -= 5
        output.seek(0)
        return output

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_en)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.image and hasattr(self.image, "file"):
            img_io = self.compress_to_webp(self.image)
            new_name = f"{slugify(self.title_en)}.webp"
            self.image.save(new_name, ContentFile(img_io.read()), save=False)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class CompanyInfo(models.Model):
    email = models.EmailField()
    mobile_no_en = models.CharField(max_length=15, blank=True)
    mobile_no_bn = models.CharField(max_length=15, blank=True)
    location_en = models.CharField(max_length=100, blank=True)
    location_bn = models.CharField(max_length=100, blank=True)

    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    def __str__(self):
        return self.email
    
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    