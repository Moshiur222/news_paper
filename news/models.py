from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import models


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


from django.db import models
from django.utils.text import slugify


# ================= LOCATION =================
class Location(models.Model):
    name_en = models.CharField(max_length=50, default="Unknown")
    name_bn = models.CharField(max_length=50, default="অজানা")

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


# ================= HERO SECTION =================
class HeroSection(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    title_en = models.CharField(max_length=150, default="Title")
    title_bn = models.CharField(max_length=150, default="শিরোনাম")

    image = models.ImageField(upload_to="hero_image/")

    description_en = models.TextField(null=True, blank=True)
    description_bn = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title_en


# ================= NEWS =================
class News(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="news")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="news")

    title_en = models.CharField(max_length=150, default="News Title")
    title_bn = models.CharField(max_length=150, default="খবরের শিরোনাম")

    slug = models.SlugField(unique=True, blank=True)

    image = models.ImageField(upload_to="news/")

    description_en = models.TextField(null=True, blank=True)
    description_bn = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_en)
            slug = base_slug
            counter = 1

            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_en