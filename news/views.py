from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from collections import defaultdict
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import *
import json





def home(request):
    current_language = request.session.get('language', 'bn')

    dhaka_location = Location.objects.filter(name_en='Dhaka').first()
    if dhaka_location:
        dhaka_name = dhaka_location.name_bn if current_language == 'bn' else dhaka_location.name_en
    else:
        dhaka_name = 'ঢাকা' if current_language == 'bn' else 'Dhaka'

    categories = Category.objects.prefetch_related(
        'news'
    ).all()
    context = {
        'current_language': current_language,
        'dhaka': dhaka_name,
        'categories': categories,
    }

    return render(request, 'news/landing/pages/home.html', context)

def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Email is required")
        elif Subscriber.objects.filter(email=email).exists():
            messages.warning(request, "You are already subscribed!")
        else:
            Subscriber.objects.create(email=email)
            messages.success(request, "Subscribed successfully!")

    return redirect(request.META.get("HTTP_REFERER", "/"))

def category_news(request, slug):
    category = get_object_or_404(Category, slug=slug)

    news = (
        News.objects
        .filter(category=category)
        .select_related('category', 'location')
        .order_by('-created_at')
    )

    return render(request, 'news/landing/pages/category_news.html', {
        'category': category,
        'news': news,
        'active_url': slug
    })

def location_news(request, slug):
    location = get_object_or_404(Location, slug=slug)

    news_list = ( 
        News.objects
        .filter(location=location)
        .select_related('category', 'location')
        .order_by('-created_at')
    )

    return render(request, 'news/landing/pages/location_news.html', {
        'location': location,
        'news_list': news_list,  
        'active_url': slug
    })


def news_view(request, slug):
    news = get_object_or_404(News, slug=slug)
    category_slug = news.category.slug if news.category else None
    
    # ========== POLL DATA LOAD ==========
    content_type = ContentType.objects.get_for_model(News)
    poll = Poll.objects.filter(content_type=content_type, object_id=news.id).first()
    
    poll_data = None
    user_has_voted = False
    poll_results = []
    total_votes = 0
    
    if poll:
        options = poll.options.all()
        total_votes = sum(opt.votes for opt in options)
        
        # Check if current user has voted (by IP or logged in user)
        ip_address = request.META.get('REMOTE_ADDR')
        if request.user.is_authenticated:
            user_vote = PollVote.objects.filter(
                poll=poll, 
                user=request.user
            ).first()
        else:
            user_vote = PollVote.objects.filter(
                poll=poll, 
                ip_address=ip_address
            ).first()
        
        user_has_voted = user_vote is not None
        
        # Calculate results for each option
        for opt in options:
            percentage = (opt.votes / total_votes * 100) if total_votes > 0 else 0
            poll_results.append({
                'id': opt.id,
                'option_en': opt.option_en,
                'option_bn': opt.option_bn,
                'votes': opt.votes,
                'percentage': round(percentage, 1),
                'is_selected': user_vote and user_vote.option.id == opt.id if user_vote else False
            })
        
        poll_data = {
            'id': poll.id,
            'question_en': poll.question_en,
            'question_bn': poll.question_bn,
            'total_votes': total_votes,
            'user_has_voted': user_has_voted,
            'options': poll_results
        }
    
    # ========== COMMENTS LOAD ==========
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=news.id
    ).select_related().order_by('-created_at')
    
    # Process comments with reply counts
    comments_list = []
    for comment in comments:
        comments_list.append({
            'id': comment.id,
            'name': comment.name,
            'message': comment.message,
            'created_at': comment.created_at,
            'replies': comment.replies.all().order_by('created_at') if hasattr(comment, 'replies') else []
        })
    
    context = {
        'news': news,
        'active_url': category_slug,
        'categories': Category.objects.all(),
        'top_newses': News.objects.filter(is_breaking=True).order_by('-id')[:10],
        'trending_news': TrandingNews.objects.all().order_by('-id')[:10],
        'tags_news': Tag.objects.all().order_by('-id')[:10],
        'latest_news': News.objects.exclude(id=news.id).order_by('-id')[:10],
        
        # Poll context
        'poll': poll_data,
        'total_votes': total_votes,
        'user_has_voted': user_has_voted,
        
        # Comments context
        'comments_list': comments_list,
        'comments_count': len(comments_list),
        
        # Current language (if you have language support)
        'current_language': request.session.get('language', 'bn'),
    }
    
    return render(request, 'news/landing/pages/news_details.html', context)


# ========== API VIEWS FOR POLL AND COMMENT ==========
@require_POST
@csrf_exempt
def submit_poll_vote(request):
    """Handle poll vote submission"""
    try:
        data = json.loads(request.body)
        poll_id = data.get('poll_id')
        option_id = data.get('option_id')
        
        poll = get_object_or_404(Poll, id=poll_id)
        option = get_object_or_404(PollOption, id=option_id)
        
        # Check for duplicate vote
        ip_address = request.META.get('REMOTE_ADDR')
        
        if request.user.is_authenticated:
            existing_vote = PollVote.objects.filter(
                poll=poll, 
                user=request.user
            ).first()
        else:
            existing_vote = PollVote.objects.filter(
                poll=poll, 
                ip_address=ip_address
            ).first()
        
        if existing_vote:
            return JsonResponse({
                'success': False, 
                'error': 'You have already voted on this poll!'
            }, status=400)
        
        # Save the vote
        PollVote.objects.create(
            poll=poll,
            option=option,
            ip_address=ip_address,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Update option vote count
        option.votes += 1
        option.save()
        
        # Get updated results
        options = poll.options.all()
        total_votes = sum(opt.votes for opt in options)
        
        results = []
        for opt in options:
            percentage = (opt.votes / total_votes * 100) if total_votes > 0 else 0
            results.append({
                'id': opt.id,
                'votes': opt.votes,
                'percentage': round(percentage, 1)
            })
        
        return JsonResponse({
            'success': True,
            'total_votes': total_votes,
            'results': results,
            'message': 'Thank you for your vote!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def submit_comment(request):
    """Handle comment submission"""
    try:
        data = json.loads(request.body)
        news_id = data.get('news_id')
        name = data.get('name')
        message = data.get('message')
        
        if not name or not message:
            return JsonResponse({
                'success': False, 
                'error': 'Name and message are required'
            }, status=400)
        
        news = get_object_or_404(News, id=news_id)
        content_type = ContentType.objects.get_for_model(News)
        
        comment = Comment.objects.create(
            name=name.strip(),
            message=message.strip(),
            content_type=content_type,
            object_id=news.id
        )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'name': comment.name,
                'message': comment.message,
                'created_at': comment.created_at.strftime("%d %b %Y, %I:%M %p"),
                'avatar': comment.name[0].upper()
            },
            'message': 'Comment posted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def get_poll_results(request):
    """Get poll results without voting"""
    try:
        data = json.loads(request.body)
        poll_id = data.get('poll_id')
        
        poll = get_object_or_404(Poll, id=poll_id)
        options = poll.options.all()
        total_votes = sum(opt.votes for opt in options)
        
        results = []
        for opt in options:
            percentage = (opt.votes / total_votes * 100) if total_votes > 0 else 0
            results.append({
                'id': opt.id,
                'votes': opt.votes,
                'percentage': round(percentage, 1)
            })
        
        return JsonResponse({
            'success': True,
            'total_votes': total_votes,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def trending_news(request, slug):
    """Trending news detail view with poll and comment system"""
    try:
        news = get_object_or_404(TrandingNews, slug=slug)
    except:
        messages.error(request, "The news you are looking for does not exist!")
        return redirect('home')  # home page এ redirect করুন
    
    # ========== POLL DATA LOAD ==========
    content_type = ContentType.objects.get_for_model(TrandingNews)
    poll = Poll.objects.filter(content_type=content_type, object_id=news.id).first()
    
    poll_data = None
    user_has_voted = False
    
    if poll:
        options = poll.options.all()
        total_votes = sum(opt.votes for opt in options)
        
        # Check if user has voted
        ip_address = request.META.get('REMOTE_ADDR')
        if request.user.is_authenticated:
            user_vote = PollVote.objects.filter(poll=poll, user=request.user).first()
        else:
            user_vote = PollVote.objects.filter(poll=poll, ip_address=ip_address).first()
        
        user_has_voted = user_vote is not None
        
        poll_options = []
        for opt in options:
            percentage = (opt.votes / total_votes * 100) if total_votes > 0 else 0
            poll_options.append({
                'id': opt.id,
                'option_en': opt.option_en,
                'option_bn': opt.option_bn,
                'votes': opt.votes,
                'percentage': round(percentage, 1),
            })
        
        poll_data = {
            'id': poll.id,
            'question_en': poll.question_en,
            'question_bn': poll.question_bn,
            'options': poll_options,
            'total_votes': total_votes,
            'user_has_voted': user_has_voted
        }
    
    # ========== COMMENTS LOAD ==========
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=news.id
    ).order_by('-created_at')
    
    comments_list = []
    for comment in comments:
        comments_list.append({
            'id': comment.id,
            'name': comment.name,
            'message': comment.message,
            'created_at': comment.created_at,
            'replies': []
        })
        
        # Add replies if any
        if hasattr(comment, 'replies'):
            for reply in comment.replies.all().order_by('created_at'):
                comments_list[-1]['replies'].append({
                    'id': reply.id,
                    'name': reply.name,
                    'message': reply.message,
                    'created_at': reply.created_at
                })
    
    # Sidebar data
    categories = Category.objects.all()
    top_newses = News.objects.filter(is_breaking=True).order_by('-id')[:10]
    trending_news_list = TrandingNews.objects.all().order_by('-id')[:10]
    latest_news_list = News.objects.all().order_by('-id')[:10]
    
    context = {
        'news': news,
        'categories': categories,
        'top_newses': top_newses,
        'trending_news': trending_news_list,
        'latest_news': latest_news_list,
        'active_url': None,
        'poll': poll_data,
        'comments_list': comments_list,
        'comments_count': len(comments_list),
        'current_language': request.session.get('language', 'bn'),
    }
    
    return render(request, 'news/landing/pages/Trending_news_details.html', context)

def tag_news(request, slug):
    tags = get_object_or_404(Tag, slug=slug)

    news_list = (News.objects.filter(tags=tags).order_by('-created_at'))
    return render(request, 'news/landing/pages/tag_news.html', {
        'tags': tags,
        'news_list': news_list,  
        'active_url': slug
    })

# ========== COMMENT REPLY VIEW ==========

@require_POST
@csrf_exempt
def submit_comment_reply(request):
    """Handle comment reply submission"""
    try:
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        name = data.get('name')
        message = data.get('message')
        
        if not name or not message:
            return JsonResponse({
                'success': False, 
                'error': 'Name and message are required'
            }, status=400)
        
        parent_comment = get_object_or_404(Comment, id=comment_id)
        
        # Create reply (assuming you have CommentReply model)
        from news.models import CommentReply
        reply = CommentReply.objects.create(
            comment=parent_comment,
            name=name.strip(),
            message=message.strip()
        )
        
        return JsonResponse({
            'success': True,
            'reply': {
                'id': reply.id,
                'name': reply.name,
                'message': reply.message,
                'created_at': reply.created_at.strftime("%d %b %Y, %I:%M %p"),
                'avatar': reply.name[0].upper()
            },
            'message': 'Reply posted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def get_comment_replies(request):
    """Get replies for a comment"""
    try:
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        
        comment = get_object_or_404(Comment, id=comment_id)
        replies = comment.replies.all().order_by('created_at')
        
        replies_list = []
        for reply in replies:
            replies_list.append({
                'id': reply.id,
                'name': reply.name,
                'message': reply.message,
                'created_at': reply.created_at.strftime("%d %b %Y, %I:%M %p"),
                'avatar': reply.name[0].upper()
            })
        
        return JsonResponse({
            'success': True,
            'replies': replies_list
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
# for admin panel

def admin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "news/admin/pages/login.html")


@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("admin")
    
    # ========== STATS CARDS এর জন্য ডাটা ==========
    total_users = User.objects.count()
    total_news = News.objects.count()
    total_trending = TrandingNews.objects.count()
    total_subscribers = Subscriber.objects.count()
    
    # গত মাসের তুলনায় পরিবর্তন
    last_month = timezone.now() - timedelta(days=30)
    previous_month = timezone.now() - timedelta(days=60)
    
    news_last_month = News.objects.filter(created_at__gte=last_month).count()
    news_previous_month = News.objects.filter(created_at__gte=previous_month, created_at__lt=last_month).count()
    
    if news_previous_month > 0:
        news_growth = round(((news_last_month - news_previous_month) / news_previous_month) * 100, 1)
    else:
        news_growth = 12.5
    
    # ========== চার্টের জন্য ডাটা (Last 7 days) ==========
    chart_labels = []
    chart_data = []
    
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        chart_labels.append(date.strftime('%a, %b %d'))
        count = News.objects.filter(created_at__date=date.date()).count()
        chart_data.append(count)
    
    # ক্যাটাগরি ভিত্তিক নিউজ কাউন্ট - আলাদা লিস্ট তৈরি করুন
    category_names = []
    category_counts = []
    
    for category in Category.objects.all()[:6]:
        category_names.append(category.name_en)
        category_counts.append(category.news.count())
    
    # ========== রিসেন্ট নিউজ ==========
    recent_news = News.objects.select_related('category', 'location').order_by('-created_at')[:8]
    
    # ========== টপ ক্যাটাগরি ==========
    top_categories = Category.objects.annotate(
        news_count=Count('news')
    ).order_by('-news_count')[:5]
    
    # ========== প্রোগ্রেস আইটেম (News by Location) ==========
    location_progress = []
    for location in Location.objects.all()[:4]:
        count = location.news.count()
        total = News.objects.count()
        percentage = int((count / total) * 100) if total > 0 else 0
        location_progress.append({
            'name': location.name_en,
            'count': count,
            'percentage': percentage
        })
    
    # ========== টিম মেম্বারস ==========
    team_members = User.objects.filter(is_staff=True)[:4]
    
    context = {
        # Stats Cards
        'total_users': total_users,
        'total_news': total_news,
        'total_trending': total_trending,
        'total_subscribers': total_subscribers,
        'news_growth': news_growth,
        
        # Charts - সরাসরি লিস্ট পাঠান
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'category_names': category_names,  
        'category_counts': category_counts, 
        
        # Recent News Table
        'recent_news': recent_news,
        
        # Top Categories
        'top_categories': top_categories,
        
        # Progress Items
        'location_progress': location_progress,
        
        # Team Members
        'team_members': team_members,
        
        # Browser Stats
        'browser_stats': [
            {'name': 'Chrome', 'icon': 'chrome', 'percent': 64},
            {'name': 'Safari', 'icon': 'safari', 'percent': 19},
            {'name': 'Firefox', 'icon': 'firefox', 'percent': 12},
            {'name': 'Edge', 'icon': 'edge', 'percent': 5},
        ],
    }
    
    return render(request, "news/admin/pages/dashboard.html", context)


def logout_view(request):
    logout(request)
    return redirect("admin")

@login_required
def admin_location_list(request):

    if not request.user.is_authenticated:
        return redirect("admin")
    locations = Location.objects.all().order_by('id')
    errors = {}
 
    # Handle form submission (Add/Edit)
    if request.method == 'POST':
        location_id = request.POST.get('location_id')
        name_en = request.POST.get('name_en', '').strip()
        name_bn = request.POST.get('name_bn', '').strip()
        
        # Validation
        if not name_en:
            errors['name_en'] = 'English name is required'
        if not name_bn:
            errors['name_bn'] = 'Bengali name is required'
        
        if not errors:
            try:
                if location_id:
                    location = get_object_or_404(Location, id=location_id)
                    location.name_en = name_en
                    location.name_bn = name_bn
                    location.save()
                    messages.success(request, 'Location updated successfully!')
                else:
                    # Add new location
                    Location.objects.create(
                        name_en=name_en,
                        name_bn=name_bn
                    )
                    messages.success(request, 'Location added successfully!')
                
                return redirect('admin_location_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
 
    context = {
        'locations': locations,
        'errors': errors,
    }
    return render(request, 'news/admin/pages/admin_location_list.html', context)
 
 
@require_http_methods(["GET"])
def get_location(request, pk):
    """
    API endpoint to get location data for editing
    """
    location = get_object_or_404(Location, pk=pk)
    data = {
        'id': location.id,
        'name_en': location.name_en,
        'name_bn': location.name_bn,
        'slug': location.slug,
    }
    return JsonResponse(data)
 
 
@require_http_methods(["POST"])
def delete_location(request, pk):
    """
    Delete a location
    """
    location = get_object_or_404(Location, pk=pk)
    location.delete()
    messages.success(request, 'Location deleted successfully!')
    return redirect('admin_location_list')


@login_required
def tags(request):

    if not request.user.is_authenticated:
        return redirect("admin")
    tag = Tag.objects.all().order_by('id')
    errors = {}
 
    # Handle form submission (Add/Edit)
    if request.method == 'POST':
        tag_id = request.POST.get('tag_id')
        name_en = request.POST.get('name_en', '').strip()
        name_bn = request.POST.get('name_bn', '').strip()
        
        # Validation
        if not name_en:
            errors['name_en'] = 'English name is required'
        if not name_bn:
            errors['name_bn'] = 'Bengali name is required'
        
        if not errors:
            try:
                if tag_id:
                    # Edit existing location
                    tag = get_object_or_404(Tag, id=tag_id)
                    tag.name_en = name_en
                    tag.name_bn = name_bn
                    tag.save()
                    messages.success(request, 'Tag updated successfully!')
                else:
                    # Add new location
                    Tag.objects.create(
                        name_en=name_en,
                        name_bn=name_bn
                    )
                    messages.success(request, 'Tag added successfully!')
                
                return redirect('tag')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
 
    context = {
        'tags': tag,
        'errors': errors,
    }
    return render(request, 'news/admin/pages/tag_list.html', context)
 
 
@require_http_methods(["GET"])
def get_tag(request, pk):
    """
    API endpoint to get location data for editing
    """
    tag = get_object_or_404(Tag, pk=pk)
    data = {
        'id': tag.id,
        'name_en': tag.name_en,
        'name_bn': tag.name_bn,
        'slug': tag.slug,
    }
    return JsonResponse(data)
 
 
@require_http_methods(["POST"])
def delete_tag(request, pk):
    """
    Delete a location
    """
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    messages.success(request, 'tag deleted successfully!')
    return redirect('tag')

from django.db.models import Exists, OuterRef
from django.contrib.contenttypes.models import ContentType


@login_required
def news(request):

    news_content_type = ContentType.objects.get_for_model(News)

    poll_subquery = Poll.objects.filter(
        content_type=news_content_type,
        object_id=OuterRef('id')
    )

    news_list = News.objects.select_related("category", "location").prefetch_related("tags").annotate(
        has_poll=Exists(poll_subquery)
    ).order_by('-id')

    categories = Category.objects.all().order_by('id')
    locations = Location.objects.all().order_by('id')
    tags = Tag.objects.all().order_by('id')  

    errors = {}

    if request.method == "POST":

        news_id = request.POST.get("news_id")
        title_en = request.POST.get("title_en", "").strip()
        title_bn = request.POST.get("title_bn", "").strip()
        description_en = request.POST.get("description_en", "").strip()
        description_bn = request.POST.get("description_bn", "").strip()
        category_id = request.POST.get("category")
        location_id = request.POST.get("location")
        is_breaking = request.POST.get("is_breaking") == "on"

        tag_ids = request.POST.getlist("tags")

        # POLL DATA
        poll_question_en = request.POST.get("poll_question_en")
        poll_question_bn = request.POST.get("poll_question_bn")
        options_en = request.POST.getlist("option_en[]")
        options_bn = request.POST.getlist("option_bn[]")

        # ---------------- VALIDATION ----------------
        if not title_en:
            errors["title_en"] = "English title is required"
        if not title_bn:
            errors["title_bn"] = "Bangla title is required"
        if not category_id:
            errors["category"] = "Category is required"
        if not location_id:
            errors["location"] = "Location is required"

        if not errors:

            category = get_object_or_404(Category, id=category_id)
            location = get_object_or_404(Location, id=location_id)

            # ================= UPDATE =================
            if news_id:
                obj = get_object_or_404(News, id=news_id)

                obj.title_en = title_en
                obj.title_bn = title_bn
                obj.description_en = description_en
                obj.description_bn = description_bn
                obj.category = category
                obj.location = location
                obj.is_breaking = is_breaking

                if request.FILES.get("image"):
                    if obj.image:
                        obj.image.delete(save=False)
                    obj.image = request.FILES.get("image")

                obj.save()

                # ✅ UPDATE TAGS
                if tag_ids:
                    obj.tags.set(tag_ids)
                else:
                    obj.tags.clear()

                news_obj = obj
                messages.success(request, "News updated successfully!")

            # ================= ADD =================
            else:
                if not request.FILES.get("image"):
                    messages.error(request, "Image is required!")
                    return redirect("news")

                news_obj = News.objects.create(
                    title_en=title_en,
                    title_bn=title_bn,
                    description_en=description_en,
                    description_bn=description_bn,
                    category=category,
                    location=location,
                    image=request.FILES.get("image"),
                    is_breaking=is_breaking
                )
                if tag_ids:
                    news_obj.tags.set(tag_ids)

                messages.success(request, "News added successfully!")

            # ================= POLL SAVE =================
            if poll_question_bn and poll_question_en and options_bn and options_en:

                valid_options = any(
                    en.strip() and bn.strip()
                    for en, bn in zip(options_en, options_bn)
                )

                if valid_options:
                    content_type = ContentType.objects.get_for_model(News)

                    Poll.objects.filter(
                        content_type=content_type,
                        object_id=news_obj.id
                    ).delete()

                    poll = Poll.objects.create(
                        question_en=poll_question_en.strip(),
                        question_bn=poll_question_bn.strip(),
                        content_type=content_type,
                        object_id=news_obj.id
                    )

                    for en, bn in zip(options_en, options_bn):
                        if en.strip() and bn.strip():
                            PollOption.objects.create(
                                poll=poll,
                                option_en=en.strip(),
                                option_bn=bn.strip()
                            )

                    messages.success(request, "Poll added successfully!")
                else:
                    messages.warning(request, "Poll not added: No valid options provided")

            else:
                if news_id:
                    content_type = ContentType.objects.get_for_model(News)
                    Poll.objects.filter(
                        content_type=content_type,
                        object_id=news_obj.id
                    ).delete()

            return redirect("news")

        else:
            messages.error(request, "Please fix errors below")

    return render(request, "news/admin/pages/news.html", {
        "news_list": news_list,
        "categories": categories,
        "locations": locations,
        "tags": tags,
        "errors": errors
    })

@require_http_methods(["GET"])
def get_news(request, pk):
    obj = get_object_or_404(News, pk=pk)

    content_type = ContentType.objects.get_for_model(News)
    poll = Poll.objects.filter(content_type=content_type, object_id=obj.id).first()

    options = []
    if poll:
        options = list(poll.options.values("option_en", "option_bn"))

    return JsonResponse({
        "id": obj.id,
        "title_en": obj.title_en,
        "title_bn": obj.title_bn,
        "description_en": obj.description_en,
        "description_bn": obj.description_bn,
        "category": obj.category.id,
        "location": obj.location.id,
        "is_breaking": obj.is_breaking,
        "image": obj.image.url if obj.image else "",

        # ✅ TAGS
        "tags": list(obj.tags.values_list("id", flat=True)),

        # POLL
        "poll_question_en": poll.question_en if poll else "",
        "poll_question_bn": poll.question_bn if poll else "",
        "options": options
    })

# ---------------- DELETE ----------------
@require_http_methods(["POST"])
def delete_news(request, pk):
    obj = get_object_or_404(News, pk=pk)

    if obj.image:
        obj.image.delete(save=False)

    obj.delete()
    messages.success(request, "News deleted successfully!")
    return redirect("news")

@login_required
def category(request):

    categories = Category.objects.all().order_by('id')
    errors = {}

    # ================= ADD / UPDATE =================
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        name_en = request.POST.get('name_en', '').strip()
        name_bn = request.POST.get('name_bn', '').strip()

        # Validation
        if not name_en:
            errors['name_en'] = 'English name is required'
        if not name_bn:
            errors['name_bn'] = 'Bengali name is required'

        if not errors:
            try:
                if category_id:
                    # UPDATE
                    category = get_object_or_404(Category, id=category_id)
                    category.name_en = name_en
                    category.name_bn = name_bn
                    category.save()

                    messages.success(request, 'Category updated successfully!')
                else:
                    # ADD
                    Category.objects.create(
                        name_en=name_en,
                        name_bn=name_bn
                    )
                    messages.success(request, 'Category added successfully!')

                return redirect('category')

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'news/admin/pages/category.html', {
        'categories': categories,
        'errors': errors,
    })


# ================= GET SINGLE CATEGORY (for edit) =================
@require_http_methods(["GET"])
def get_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    data = {
        'id': category.id,
        'name_en': category.name_en,
        'name_bn': category.name_bn,
        'slug': category.slug,
    }

    return JsonResponse(data)


# ================= DELETE CATEGORY =================
@require_http_methods(["POST"])
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()

    messages.success(request, 'Category deleted successfully!')
    return redirect('category')

@require_http_methods(["POST"])
def switch_language(request):
    language = request.POST.get('language', 'bn')
    next_url = request.POST.get('next', '/')

    if language in ['bn', 'en']:
        request.session['language'] = language

    return redirect(next_url)



@login_required
def trending(request):
    # select_related সম্পূর্ণ সরিয়ে ফেলুন
    news_list = TrandingNews.objects.all().order_by('-id')
    errors = {}

    if request.method == "POST":
        news_id = request.POST.get("news_id")
        title_en = request.POST.get("title_en", "").strip()
        title_bn = request.POST.get("title_bn", "").strip()
        description_en = request.POST.get("description_en", "").strip()
        description_bn = request.POST.get("description_bn", "").strip()

        if not title_en:
            errors["title_en"] = "English title is required"
        if not title_bn:
            errors["title_bn"] = "Bangla title is required"
            
        if not errors:
            if news_id:  # UPDATE
                obj = get_object_or_404(TrandingNews, id=news_id)
                obj.title_en = title_en
                obj.title_bn = title_bn
                obj.description_en = description_en
                obj.description_bn = description_bn

                if request.FILES.get("image"):
                    if obj.image:
                        obj.image.delete(save=False)
                    obj.image = request.FILES.get("image")

                obj.save()
                messages.success(request, "News updated successfully!")

            else:  # ADD NEW
                if not request.FILES.get("image"):
                    messages.error(request, "Image is required!")
                    return redirect("trending")

                TrandingNews.objects.create(  # ← News না, TrandingNews
                    title_en=title_en,
                    title_bn=title_bn,
                    description_en=description_en,
                    description_bn=description_bn,
                    image=request.FILES.get("image"),
                )
                messages.success(request, "News added successfully!")

            return redirect("trending")
        else:
            messages.error(request, "Please fix errors below")

    return render(request, "news/admin/pages/trending_news.html", {
        "news_list": news_list,
        "errors": errors
    })
# ---------------- GET SINGLE NEWS ----------------
@require_http_methods(["GET"])
def get_trending_news(request, pk):
    obj = get_object_or_404(TrandingNews, pk=pk)

    return JsonResponse({
    "id": obj.id,
    "title_en": obj.title_en,
    "title_bn": obj.title_bn,
    "description_en": obj.description_en,
    "description_bn": obj.description_bn,
    "image": obj.image.url if obj.image else ""
})

# ---------------- DELETE ----------------
@require_http_methods(["POST"])
def delete_trending_news(request, pk):
    obj = get_object_or_404(TrandingNews, pk=pk)

    if obj.image:
        obj.image.delete(save=False)

    obj.delete()
    messages.success(request, "News deleted successfully!")
    return redirect("trending")


@login_required
def company_info(request):
    company = CompanyInfo.objects.first()
    errors = {}

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        mobile_no_en = request.POST.get("mobile_no_en", "").strip()
        mobile_no_bn = request.POST.get("mobile_no_bn", "").strip()

        location_en = request.POST.get("location_en", "").strip()
        location_bn = request.POST.get("location_bn", "").strip()

        facebook = request.POST.get("facebook", "").strip()
        twitter = request.POST.get("twitter", "").strip()
        instagram = request.POST.get("instagram", "").strip()
        linkedin = request.POST.get("linkedin", "").strip()
        youtube = request.POST.get("youtube", "").strip()

        # Validation
        if not email:
            errors["email"] = "Email is required"

        if not errors:
            if company:  # UPDATE
                company.email = email
                company.mobile_no_en = mobile_no_en
                company.mobile_no_bn = mobile_no_bn
                company.location_en = location_en
                company.location_bn = location_bn

                company.facebook = facebook
                company.twitter = twitter
                company.instagram = instagram
                company.linkedin = linkedin
                company.youtube = youtube

                company.save()
                messages.success(request, "Company info updated successfully!")

            else:  # CREATE
                CompanyInfo.objects.create(
                    email=email,
                    mobile_no_en=mobile_no_en,
                    mobile_no_bn=mobile_no_bn,
                    location_en=location_en,
                    location_bn=location_bn,
                    facebook=facebook,
                    twitter=twitter,
                    instagram=instagram,
                    linkedin=linkedin,
                    youtube=youtube,
                )

                messages.success(request, "Company info created successfully!")

            return redirect("company_info")

        else:
            messages.error(request, "Please fix errors below")

    return render(request, "news/admin/pages/company_info.html", {
        "company": company,
        "errors": errors
    })

@login_required
def subscribers(request):
    subscribers = Subscriber.objects.all().order_by('-id')

    return render(request, "news/admin/pages/subscriber.html", {
        'subscribers': subscribers
    })