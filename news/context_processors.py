from .models import *

def locations(request):
    return {
        'locations': Location.objects.all()
    }
def active_menu(request):
    url_name = ""

    if request.resolver_match:
        url_name = request.resolver_match.url_name or ""

    return {
        'active_url': url_name
    }

def get_translations(request):
    lang = request.session.get('language', 'bn')

    translations = {

        # ================= BANGLA =================
        'bn': {

            # Top Bar
            'dhaka': 'ঢাকা',
            'bangla': 'বাংলা',
            'english': 'English',

            # Navbar
            'home': 'হোম',
            'national': 'জাতীয়',
            'politics': 'রাজনীতি',
            'international': 'আন্তর্জাতিক',
            'economy': 'অর্থ-বাণিজ্য',
            'sports': 'খেলাধুলা',
            'entertainment': 'বিনোদন',
            'technology': 'প্রযুক্তি',
            'opinion': 'মতামত',
            'top_news': 'সবার শীর্ষে',
            'country': 'সারা দেশ',
            'search': 'খুঁজুন...',

            # Footer
            'main_sections': 'প্রধান বিভাগ',
            'others': 'অন্যান্য',
            'lifestyle': 'লাইফস্টাইল',
            'newsletter': 'নিউজলেটার সাবস্ক্রাইব',
            'email_placeholder': 'আপনার ইমেইল লিখুন',
            'subscribe': 'সাবস্ক্রাইব',
            'copyright': 'সর্বস্বত্ব সংরক্ষিত',

            # Common
            'read_more': 'বিস্তারিত',
            'view_all': 'সব দেখুন',
            'no_data': 'কোন তথ্য পাওয়া যায়নি',

            # ======= CATEGORY STRIP (NEW) =======
            'world': 'বিশ্ব',
            'trade': 'বাণিজ্য',
            'health': 'স্বাস্থ্য',
            'law_court': 'আইন ও আদালত',
            'education': 'শিক্ষা',
            'climate': 'জলবায়ু',
            'transport': 'যাতায়াত',
            'tech': 'টেক',
        },

        # ================= ENGLISH =================
        'en': {

            # Top Bar
            'dhaka': 'Dhaka',
            'bangla': 'বাংলা',
            'english': 'English',

            # Navbar
            'home': 'Home',
            'national': 'National',
            'politics': 'Politics',
            'international': 'International',
            'economy': 'Economy',
            'sports': 'Sports',
            'entertainment': 'Entertainment',
            'technology': 'Technology',
            'opinion': 'Opinion',
            'top_news': 'Top News',
            'country': 'Country',
            'search': 'Search...',

            # Footer
            'main_sections': 'Main Sections',
            'others': 'Others',
            'lifestyle': 'Lifestyle',
            'newsletter': 'Subscribe Newsletter',
            'email_placeholder': 'Enter your email',
            'subscribe': 'Subscribe',
            'copyright': 'All Rights Reserved',

            # Common
            'read_more': 'Read More',
            'view_all': 'View All',
            'no_data': 'No data found',

            # ======= CATEGORY STRIP (NEW) =======
            'world': 'World',
            'trade': 'Trade',
            'health': 'Health',
            'law_court': 'Law & Court',
            'education': 'Education',
            'climate': 'Climate',
            'transport': 'Transport',
            'tech': 'Tech',
        }
    }

    return {
        't': translations.get(lang, translations['bn']),
        'current_language': lang,
    }