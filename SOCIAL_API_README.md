# Social Media Content Generation System - API Documentation

AI-powered social media content generation using Google's Gemini API with support for LinkedIn, Instagram, YouTube, Facebook, and Blog posts within the multi-tenant lead management system.

## 🏗️ **System Architecture**

```
Account (Root)
    ├── Companies (Multiple per account)
    │   ├── Social Generation 1 (LinkedIn - 5 unique posts)
    │   ├── Social Generation 2 (Instagram - 5 unique posts)  
    │   ├── Social Generation 3 (YouTube - 5 unique videos)
    │   └── Social Generation N...
    └── Other Companies...
```

## 📊 **Database Relationships**

```sql
accounts (1) ←→ (N) social_generations
companies (1) ←→ (N) social_generations  
users (1) ←→ (N) social_generations (requested_by)
company_banners (1) ←→ (N) social_generations (optional)
```

- **accounts.id** → **social_generations.account_id** (Foreign Key, CASCADE DELETE)
- **companies.id** → **social_generations.company_id** (Foreign Key, CASCADE DELETE)
- **users.id** → **social_generations.requested_by** (Foreign Key, Optional)
- **company_banners.id** → **social_generations.company_banner_id** (Foreign Key, SET NULL)

## 🚀 **Quick Start**

### **Prerequisites**
- Flask authentication and company management systems running
- Valid account_id and company_id from existing systems
- Supabase credentials configured in `.env`
- Google Gemini API key integrated: `AIzaSyD1vW1f-BWip1_MZcqAm2ECUhk40WNZwFU`

### **Base URL**: `http://localhost:5000`

---

## 📚 **Social Media Content Generation API**

### **1. Generate Social Media Content**
Generate AI-powered social media posts for a specific platform using Gemini 2.0-Flash.

**Endpoint**: `POST /social-generate`

**Request Body**:
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "platform": "linkedin",
  "query": "Generate professional posts about AI in digital marketing for B2B SaaS companies",
  "company_banner_id": "banner-uuid-here",
  "requested_by": "user-uuid-here",
  "include_past": false
}
```

**Required Fields**:
- `account_id`: UUID of the parent account
- `company_id`: UUID of the company (must belong to account)
- `platform`: Target platform (`linkedin`, `instagram`, `youtube`, `facebook`, `blog`)
- `query`: Content generation prompt (minimum 10 characters)

**Optional Fields**:
- `company_banner_id`: UUID of specific company banner for context
- `requested_by`: UUID of user requesting generation
- `include_past`: Boolean to include past generations in context

**Supported Platforms**:
- `linkedin`: Professional business content and networking
- `instagram`: Visual storytelling and brand narrative
- `youtube`: Video tutorials and educational content
- `facebook`: Community engagement and social interaction
- `blog`: Long-form thought leadership content

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Successfully generated 5 linkedin posts",
  "generation": {
    "id": "gen-uuid-12345",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "company_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "company_banner_id": "banner-uuid-here",
    "requested_by": "user-uuid-here",
    "platform": "linkedin",
    "query": "Generate professional posts about AI in digital marketing for B2B SaaS companies",
    "include_past": false,
    "request_payload": {
      "model": "gemini-2.0-flash",
      "prompt": "Platform: LinkedIn Professional Network...",
      "platform": "linkedin",
      "query": "Generate professional posts about AI in digital marketing for B2B SaaS companies",
      "timestamp": "2025-10-07T14:30:00Z"
    },
    "generated_posts": {
      "posts": [
        {
          "id": 1,
          "title": "AI-Powered Marketing: The B2B SaaS Revolution",
          "content": "The marketing landscape for B2B SaaS companies is undergoing a seismic shift with AI at its core. From predictive analytics that forecast customer behavior to automated personalization that speaks directly to individual pain points, AI is no longer just a competitive advantage—it's becoming essential for survival.\n\nKey areas where AI is making the biggest impact:\n🔹 Lead scoring and qualification\n🔹 Content personalization at scale\n🔹 Predictive customer lifetime value\n🔹 Automated A/B testing\n\nThe companies that embrace AI-driven marketing strategies today will be the market leaders of tomorrow.",
          "hashtags": ["#AIMarketing", "#B2BSaaS", "#MarketingAutomation", "#DigitalTransformation", "#SaaS"],
          "call_to_action": "How is your B2B SaaS company leveraging AI in marketing? Share your experiences below!",
          "post_type": "professional_insight"
        },
        {
          "id": 2,
          "title": "5 AI Marketing Tools Every B2B SaaS Should Consider",
          "content": "As a B2B SaaS professional, I've seen firsthand how the right AI marketing tools can transform your entire customer acquisition strategy. Here are 5 categories that are game-changers:\n\n1️⃣ Conversational AI for lead qualification\n2️⃣ Predictive analytics for churn prevention\n3️⃣ AI-powered content generation for scale\n4️⃣ Intelligent email marketing optimization\n5️⃣ Dynamic pricing and proposal optimization\n\nThe key isn't just adopting AI—it's choosing the right tools that align with your specific customer journey and business model.",
          "hashtags": ["#MarTech", "#AITools", "#B2BMarketing", "#SaaS", "#MarketingStrategy"],
          "call_to_action": "Which AI marketing tools have made the biggest impact in your organization?",
          "post_type": "professional_insight"
        }
      ]
    },
    "status": "completed",
    "error": null,
    "created_at": "2025-10-07T14:30:00Z",
    "completed_at": "2025-10-07T14:31:15Z"
  }
}
```

**Platform-Specific Response Formats**:

**LinkedIn Posts**:
```json
{
  "id": 1,
  "title": "Professional headline for engagement",
  "content": "150-300 word professional LinkedIn post content...",
  "hashtags": ["#Professional", "#Industry", "#Business"],
  "call_to_action": "Engagement question or discussion starter",
  "post_type": "professional_insight"
}
```

**Instagram Posts**:
```json
{
  "id": 1,
  "title": "Eye-catching post title",
  "caption": "50-150 word engaging caption with emojis and personality...",
  "visual_description": "Detailed description of recommended image or video content",
  "hashtags": ["#Instagram", "#Visual", "#Brand", "#Engagement"],
  "story_ideas": ["Behind-the-scenes concept", "User-generated content idea"],
  "post_type": "visual_content"
}
```

**YouTube Videos**:
```json
{
  "id": 1,
  "title": "Compelling YouTube Video Title (60-70 characters)",
  "description": "100-200 word video description with timestamps and links...",
  "script_outline": [
    "Hook: Attention-grabbing opening (0-15 seconds)",
    "Introduction: Channel intro and video preview (15-45 seconds)",
    "Main Content: Core educational content (45 seconds - 8 minutes)",
    "Call to Action: Subscribe, comment, like (final 15 seconds)"
  ],
  "duration_estimate": "5-10 minutes",
  "hashtags": ["#YouTube", "#Tutorial", "#Education"],
  "thumbnail_description": "Bright, high-contrast thumbnail with bold text overlay",
  "post_type": "video_content"
}
```

**Facebook Posts**:
```json
{
  "id": 1,
  "title": "Community-focused post title",
  "content": "Conversational Facebook post encouraging community interaction...",
  "engagement_type": "poll",
  "hashtags": ["#Facebook", "#Community", "#Discussion"],
  "call_to_action": "Like if you agree, comment your thoughts, share with friends!",
  "target_audience": "B2B professionals interested in marketing automation",
  "post_type": "community_engagement"
}
```

**Blog Posts**:
```json
{
  "id": 1,
  "title": "SEO-Optimized Blog Post Title",
  "meta_description": "150-160 character SEO meta description with target keywords...",
  "outline": [
    "Introduction: Hook and problem statement",
    "Main Section 1: Core concept explanation",
    "Main Section 2: Practical applications",
    "Main Section 3: Best practices and tips",
    "Conclusion: Key takeaways and next steps"
  ],
  "key_points": ["Primary insight 1", "Primary insight 2", "Primary insight 3"],
  "word_count_estimate": "1500-2000 words",
  "hashtags": ["#BlogPost", "#ContentMarketing", "#SEO"],
  "cta": "Subscribe to our newsletter for weekly marketing insights",
  "post_type": "long_form_content"
}
```

**Error Responses**:
```json
// Missing required fields (400)
{
  "success": false,
  "message": "Missing required fields: platform, query",
  "generation": null
}

// Invalid platform (400)
{
  "success": false,
  "message": "Invalid platform. Must be one of: linkedin, instagram, youtube, facebook, blog",
  "generation": null
}

// Account not found (400)
{
  "success": false,
  "message": "Account not found",
  "generation": null
}

// Company doesn't belong to account (400)
{
  "success": false,
  "message": "Company does not belong to the specified account",
  "generation": null
}

// AI generation failed (400)
{
  "success": false,
  "message": "AI generation failed: Invalid response format from Gemini API",
  "generation": {
    "id": "gen-uuid-failed",
    "status": "failed"
  }
}
```

### **2. Get Social Media Generation**
Retrieve a specific generation by ID with full details including generated content.

**Endpoint**: `GET /social-generations/{generation_id}`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Generation retrieved successfully",
  "generation": {
    "id": "gen-uuid-12345",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "company_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "platform": "linkedin",
    "query": "Original query text",
    "generated_posts": {
      "posts": [
        {
          "id": 1,
          "title": "Generated post title",
          "content": "Full post content...",
          "hashtags": ["#Tag1", "#Tag2"],
          "call_to_action": "Engagement question"
        }
      ]
    },
    "status": "completed",
    "created_at": "2025-10-07T14:30:00Z",
    "completed_at": "2025-10-07T14:31:15Z"
  }
}
```

### **3. Get Generations by Account**
Retrieve all generations for an account with optional platform filtering.

**Endpoint**: `GET /accounts/{account_id}/social-generations`

**Query Parameters**:
- `platform` (optional): Filter by specific platform

**Examples**:
- `GET /accounts/{account_id}/social-generations` - All generations
- `GET /accounts/{account_id}/social-generations?platform=linkedin` - LinkedIn only
- `GET /accounts/{account_id}/social-generations?platform=instagram` - Instagram only

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Retrieved 25 generations",
  "generations": [
    {
      "id": "gen-uuid-1",
      "company_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "platform": "linkedin", 
      "query": "AI marketing posts for B2B SaaS",
      "status": "completed",
      "created_at": "2025-10-07T14:30:00Z",
      "completed_at": "2025-10-07T14:31:15Z"
    },
    {
      "id": "gen-uuid-2",
      "company_id": "company-uuid-2",
      "platform": "instagram",
      "query": "Brand storytelling for tech startup",
      "status": "completed", 
      "created_at": "2025-10-07T13:15:00Z",
      "completed_at": "2025-10-07T13:16:30Z"
    }
  ]
}
```

### **4. Get Generations by Company**
Retrieve all generations for a specific company across all platforms.

**Endpoint**: `GET /companies/{company_id}/social-generations`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Retrieved 12 generations for company",
  "generations": [
    {
      "id": "gen-uuid-1",
      "account_id": "550e8400-e29b-41d4-a716-446655440000",
      "platform": "youtube",
      "query": "Product tutorial videos for SaaS onboarding", 
      "status": "completed",
      "generated_posts": {
        "posts": [
          {
            "id": 1,
            "title": "SaaS Onboarding: First 5 Minutes That Matter",
            "duration_estimate": "8-10 minutes"
          }
        ]
      },
      "created_at": "2025-10-07T12:00:00Z",
      "completed_at": "2025-10-07T12:02:45Z"
    }
  ]
}
```

### **5. Delete Social Media Generation**
Delete a specific generation and all its generated content.

**Endpoint**: `DELETE /social-generations/{generation_id}`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Generation deleted successfully"
}
```

**Error Response (404)**:
```json
{
  "success": false,
  "message": "Generation not found"
}
```

### **6. Get Supported Platforms**
Retrieve list of all supported social media platforms with descriptions.

**Endpoint**: `GET /social-platforms`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Supported social media platforms",
  "platforms": [
    {
      "id": "linkedin",
      "name": "LinkedIn",
      "description": "Professional networking and business content",
      "content_types": ["Professional insights", "Industry trends", "Business tips", "Thought leadership"],
      "optimal_length": "150-300 words",
      "hashtag_count": "3-5 hashtags"
    },
    {
      "id": "instagram",
      "name": "Instagram",
      "description": "Visual storytelling and brand narrative",
      "content_types": ["Visual stories", "Behind-the-scenes", "Product showcases", "User engagement"],
      "optimal_length": "50-150 words",
      "hashtag_count": "5-10 hashtags"
    },
    {
      "id": "youtube",
      "name": "YouTube",
      "description": "Video content and tutorials",
      "content_types": ["Educational tutorials", "Product demos", "Industry analysis", "Case studies"],
      "optimal_length": "5-15 minutes",
      "hashtag_count": "3-5 hashtags"
    },
    {
      "id": "facebook",
      "name": "Facebook",
      "description": "Community engagement and social interaction",
      "content_types": ["Community discussions", "Event promotion", "Customer stories", "Interactive polls"],
      "optimal_length": "80-200 words",
      "hashtag_count": "3-7 hashtags"
    },
    {
      "id": "blog",
      "name": "Blog Posts",
      "description": "Long-form content and thought leadership",
      "content_types": ["In-depth analysis", "How-to guides", "Case studies", "Industry insights"],
      "optimal_length": "1500-3000 words",
      "hashtag_count": "5-8 hashtags"
    }
  ]
}
```

---

## 🧪 **Complete Testing Workflow**

### **Prerequisites Setup**
First, ensure you have valid account and company IDs:

```bash
# 1. Create user account (also creates account)
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "socialmedia@example.com",
    "password": "password123",
    "full_name": "Social Media Manager",
    "account_name": "Digital Marketing Agency"
  }'

# Note the account_id from response

# 2. Create a company
curl -X POST http://localhost:5000/companies \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "name": "TechCorp Solutions",
    "domain": "techcorp.com",
    "description": "B2B SaaS company specializing in marketing automation and lead generation"
  }'

# Note the company_id from response for following tests
```

### **Step 1: Generate LinkedIn Content**
```bash
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_id": "YOUR_COMPANY_ID", 
    "platform": "linkedin",
    "query": "Create professional posts about AI-powered lead generation for B2B SaaS companies. Focus on practical tips, industry insights, and thought leadership content.",
    "include_past": false
  }'
```

### **Step 2: Generate Instagram Content**
```bash
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_id": "YOUR_COMPANY_ID",
    "platform": "instagram", 
    "query": "Behind-the-scenes content showcasing our SaaS development team, company culture, and product development process. Include visual storytelling elements.",
    "include_past": false
  }'
```

### **Step 3: Generate YouTube Content**
```bash
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_id": "YOUR_COMPANY_ID",
    "platform": "youtube",
    "query": "Educational tutorial videos explaining how to set up marketing automation workflows for small businesses. Include step-by-step guides and best practices.",
    "include_past": false
  }'
```

### **Step 4: Generate Facebook Content**
```bash
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID", 
    "company_id": "YOUR_COMPANY_ID",
    "platform": "facebook",
    "query": "Community engagement posts about marketing challenges faced by small businesses and how our SaaS solutions help solve them. Include success stories.",
    "include_past": false
  }'
```

### **Step 5: Generate Blog Content**
```bash
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_id": "YOUR_COMPANY_ID", 
    "platform": "blog",
    "query": "In-depth articles about the future of marketing automation, AI trends in B2B sales, and comprehensive guides for lead nurturing strategies.",
    "include_past": false
  }'
```

### **Step 6: Get All Generations for Account**
```bash
curl http://localhost:5000/accounts/YOUR_ACCOUNT_ID/social-generations
```

### **Step 7: Get Platform-Specific Generations**
```bash
# Get only LinkedIn generations
curl "http://localhost:5000/accounts/YOUR_ACCOUNT_ID/social-generations?platform=linkedin"

# Get only Instagram generations
curl "http://localhost:5000/accounts/YOUR_ACCOUNT_ID/social-generations?platform=instagram"

# Get only YouTube generations
curl "http://localhost:5000/accounts/YOUR_ACCOUNT_ID/social-generations?platform=youtube"
```

### **Step 8: Get Generations by Company**
```bash
curl http://localhost:5000/companies/YOUR_COMPANY_ID/social-generations
```

### **Step 9: Get Specific Generation Details**
```bash
curl http://localhost:5000/social-generations/GENERATION_ID_FROM_STEP_1
```

### **Step 10: Get Supported Platforms**
```bash
curl http://localhost:5000/social-platforms
```

### **Step 11: Test Advanced Generation with Banner**
```bash
# First create a company banner
curl -X POST http://localhost:5000/company-banners \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "YOUR_COMPANY_ID",
    "name": "TechCorp - Social Media Banner",
    "logo_url": "https://techcorp.com/social-logo.png",
    "signature": "Follow us for more insights!\n@TechCorpSolutions",
    "metadata": {
      "purpose": "Social media campaigns",
      "department": "Marketing"
    }
  }'

# Then generate content with banner context
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_id": "YOUR_COMPANY_ID",
    "platform": "linkedin",
    "query": "Thought leadership content about the intersection of AI and customer success in B2B SaaS",
    "company_banner_id": "BANNER_ID_FROM_ABOVE",
    "requested_by": "USER_ID_IF_AVAILABLE",
    "include_past": false
  }'
```

### **Step 12: Test Error Cases**
```bash
# Invalid platform
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_id": "YOUR_COMPANY_ID",
    "platform": "tiktok",
    "query": "Test query"
  }'

# Missing required fields
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "platform": "linkedin"
  }'

# Invalid account ID
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "invalid-uuid-12345",
    "company_id": "YOUR_COMPANY_ID",
    "platform": "linkedin",
    "query": "Test query"
  }'

# Query too short
curl -X POST http://localhost:5000/social-generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_id": "YOUR_COMPANY_ID",
    "platform": "linkedin",
    "query": "short"
  }'
```

### **Step 13: Delete Generation**
```bash
curl -X DELETE http://localhost:5000/social-generations/GENERATION_ID_TO_DELETE
```

---

## 🔧 **Integration Examples**

### **JavaScript Frontend Integration**
```javascript
class SocialContentService {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async generateContent(contentData) {
    const response = await fetch(`${this.baseURL}/social-generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contentData)
    });
    return await response.json();
  }

  async getGenerations(accountId, platform = null) {
    const url = platform 
      ? `${this.baseURL}/accounts/${accountId}/social-generations?platform=${platform}`
      : `${this.baseURL}/accounts/${accountId}/social-generations`;
    
    const response = await fetch(url);
    return await response.json();
  }

  async getGeneration(generationId) {
    const response = await fetch(`${this.baseURL}/social-generations/${generationId}`);
    return await response.json();
  }

  async getCompanyGenerations(companyId) {
    const response = await fetch(`${this.baseURL}/companies/${companyId}/social-generations`);
    return await response.json();
  }

  async deleteGeneration(generationId) {
    const response = await fetch(`${this.baseURL}/social-generations/${generationId}`, {
      method: 'DELETE'
    });
    return await response.json();
  }

  async getSupportedPlatforms() {
    const response = await fetch(`${this.baseURL}/social-platforms`);
    return await response.json();
  }
}

// Usage Example
const socialService = new SocialContentService();

// Generate LinkedIn content
const linkedInResult = await socialService.generateContent({
  account_id: 'account-uuid',
  company_id: 'company-uuid',
  platform: 'linkedin',
  query: 'Professional posts about digital marketing trends for B2B SaaS companies in 2025. Focus on AI integration and customer success strategies.',
  include_past: false
});

if (linkedInResult.success) {
  const posts = linkedInResult.generation.generated_posts.posts;
  console.log(`Generated ${posts.length} LinkedIn posts`);
  
  // Display each post
  posts.forEach((post, index) => {
    console.log(`\n--- Post ${index + 1} ---`);
    console.log(`Title: ${post.title}`);
    console.log(`Content: ${post.content.substring(0, 100)}...`);
    console.log(`Hashtags: ${post.hashtags.join(' ')}`);
    console.log(`CTA: ${post.call_to_action}`);
  });
}

// Get all Instagram generations for account
const instagramGens = await socialService.getGenerations('account-uuid', 'instagram');
console.log(`Found ${instagramGens.generations.length} Instagram generations`);

// Get supported platforms with details
const platforms = await socialService.getSupportedPlatforms();
platforms.platforms.forEach(platform => {
  console.log(`${platform.name}: ${platform.description}`);
  console.log(`Optimal length: ${platform.optimal_length}`);
  console.log(`Hashtags: ${platform.hashtag_count}\n`);
});
```

### **Python Client Integration**
```python
import requests
import json
from typing import Dict, List, Optional

class SocialContentClient:
    def __init__(self, base_url: str = 'http://localhost:5000'):
        self.base_url = base_url

    def generate_content(self, **kwargs) -> Dict:
        """Generate social media content"""
        response = requests.post(f'{self.base_url}/social-generate', json=kwargs)
        return response.json()

    def get_generations(self, account_id: str, platform: Optional[str] = None) -> Dict:
        """Get generations for account, optionally filtered by platform"""
        url = f'{self.base_url}/accounts/{account_id}/social-generations'
        params = {'platform': platform} if platform else {}
        response = requests.get(url, params=params)
        return response.json()

    def get_generation(self, generation_id: str) -> Dict:
        """Get specific generation by ID"""
        response = requests.get(f'{self.base_url}/social-generations/{generation_id}')
        return response.json()

    def get_company_generations(self, company_id: str) -> Dict:
        """Get all generations for a company"""
        response = requests.get(f'{self.base_url}/companies/{company_id}/social-generations')
        return response.json()

    def delete_generation(self, generation_id: str) -> Dict:
        """Delete a generation"""
        response = requests.delete(f'{self.base_url}/social-generations/{generation_id}')
        return response.json()

    def get_supported_platforms(self) -> Dict:
        """Get list of supported platforms"""
        response = requests.get(f'{self.base_url}/social-platforms')
        return response.json()

# Usage Example
client = SocialContentClient()

# Generate YouTube content
youtube_result = client.generate_content(
    account_id='account-uuid',
    company_id='company-uuid',
    platform='youtube',
    query='''Create educational video content about email marketing automation 
             for e-commerce businesses. Include practical tutorials, best practices, 
             and common mistakes to avoid. Target audience: small to medium e-commerce 
             business owners who want to improve their email marketing ROI.''',
    include_past=False
)

if youtube_result['success']:
    generation = youtube_result['generation']
    videos = generation['generated_posts']['posts']
    
    print(f"Generated {len(videos)} YouTube video concepts:")
    for i, video in enumerate(videos, 1):
        print(f"\n=== Video {i} ===")
        print(f"Title: {video['title']}")
        print(f"Duration: {video['duration_estimate']}")
        print(f"Description: {video['description'][:150]}...")
        print(f"Script Outline:")
        for step in video['script_outline']:
            print(f"  • {step}")
        print(f"Hashtags: {', '.join(video['hashtags'])}")

# Generate content for multiple platforms
platforms = ['linkedin', 'instagram', 'facebook', 'blog']
all_results = {}

for platform in platforms:
    print(f"\nGenerating {platform} content...")
    result = client.generate_content(
        account_id='account-uuid',
        company_id='company-uuid',
        platform=platform,
        query=f'Create {platform} content about customer success strategies for B2B SaaS companies. Focus on retention, onboarding, and growth.',
        include_past=False
    )
    all_results[platform] = result

# Summary of all generations
print(f"\n=== Generation Summary ===")
for platform, result in all_results.items():
    if result['success']:
        post_count = len(result['generation']['generated_posts']['posts'])
        print(f"{platform.capitalize()}: {post_count} posts generated ✅")
    else:
        print(f"{platform.capitalize()}: Failed - {result['message']} ❌")

# Get all blog generations for the account
blog_gens = client.get_generations('account-uuid', 'blog')
print(f"\nTotal blog generations: {len(blog_gens['generations'])}")

# Get supported platforms info
platforms_info = client.get_supported_platforms()
print(f"\n=== Supported Platforms ===")
for platform in platforms_info['platforms']:
    print(f"• {platform['name']}: {platform['description']}")
    print(f"  Optimal length: {platform['optimal_length']}")
    print(f"  Hashtags: {platform['hashtag_count']}")
```

### **React Component Integration**
```jsx
import React, { useState, useEffect } from 'react';
import { SocialContentService } from './socialContentService';

const SocialContentGenerator = ({ accountId, companyId }) => {
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState('linkedin');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedPosts, setGeneratedPosts] = useState(null);
  const [error, setError] = useState(null);

  const socialService = new SocialContentService();

  useEffect(() => {
    const loadPlatforms = async () => {
      try {
        const result = await socialService.getSupportedPlatforms();
        setPlatforms(result.platforms);
      } catch (err) {
        setError('Failed to load platforms');
      }
    };
    loadPlatforms();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await socialService.generateContent({
        account_id: accountId,
        company_id: companyId,
        platform: selectedPlatform,
        query: query,
        include_past: false
      });

      if (result.success) {
        setGeneratedPosts(result.generation.generated_posts.posts);
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('Failed to generate content');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="social-content-generator">
      <h2>AI Social Media Content Generator</h2>
      
      <form onSubmit={handleGenerate}>
        <div className="form-group">
          <label>Platform:</label>
          <select 
            value={selectedPlatform} 
            onChange={(e) => setSelectedPlatform(e.target.value)}
          >
            {platforms.map(platform => (
              <option key={platform.id} value={platform.id}>
                {platform.name} - {platform.description}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Content Query:</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe what kind of content you want to generate..."
            rows={4}
            required
            minLength={10}
          />
          <small>Minimum 10 characters. Be specific about your target audience and content goals.</small>
        </div>

        <button type="submit" disabled={loading || query.length < 10}>
          {loading ? 'Generating...' : 'Generate Content'}
        </button>
      </form>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {generatedPosts && (
        <div className="generated-content">
          <h3>Generated {selectedPlatform} Posts ({generatedPosts.length})</h3>
          {generatedPosts.map((post, index) => (
            <div key={post.id} className="post-card">
              <h4>Post {index + 1}: {post.title}</h4>
              
              {post.content && (
                <div className="post-content">
                  <strong>Content:</strong>
                  <p>{post.content}</p>
                </div>
              )}

              {post.caption && (
                <div className="post-caption">
                  <strong>Caption:</strong>
                  <p>{post.caption}</p>
                </div>
              )}

              {post.script_outline && (
                <div className="script-outline">
                  <strong>Script Outline:</strong>
                  <ul>
                    {post.script_outline.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="post-hashtags">
                <strong>Hashtags:</strong> {post.hashtags.join(' ')}
              </div>

              {post.call_to_action && (
                <div className="post-cta">
                  <strong>Call to Action:</strong> {post.call_to_action}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SocialContentGenerator;
```

---

## 🤖 **AI Content Generation Details**

### **Gemini AI Integration**
- **Model**: `gemini-2.0-flash` (Google's latest multimodal AI model)
- **API Key**: `AIzaSyD1vW1f-BWip1_MZcqAm2ECUhk40WNZwFU`
- **Response Format**: Structured JSON with platform-specific fields
- **Content Quality**: Professional, engaging, and platform-optimized content
- **Generation Time**: Typically 30-90 seconds per request

### **Platform-Specific AI Prompts**
Each platform uses specialized system prompts optimized for:

**LinkedIn**:
- Professional insights and industry trends
- Business tips and career advice  
- Company achievements and thought leadership
- Networking and professional engagement
- 150-300 words with 3-5 hashtags

**Instagram**:
- Visual storytelling and brand narrative
- Behind-the-scenes content ideas
- User engagement and community building
- Product/service showcases with visual descriptions
- 50-150 words with 5-10 hashtags

**YouTube**:
- Educational tutorials and how-to content
- Industry analysis and expert insights
- Product demonstrations and reviews
- Storytelling and case studies with script outlines
- 5-15 minute videos with thumbnails

**Facebook**:
- Community engagement and discussions
- Brand storytelling and company values
- Event promotion and announcements
- Customer testimonials and success stories
- Interactive polls and Q&A content

**Blog**:
- In-depth industry analysis
- Comprehensive how-to guides
- Case studies and success stories
- Opinion pieces and thought leadership
- SEO-optimized with 1500-3000 words

### **Content Uniqueness Guarantee**
- Each generation produces **exactly 5 unique posts**
- No duplicate content across the 5 posts in a single generation
- Different approaches, tones, and angles for variety
- Platform-appropriate formatting and engagement elements
- Relevant hashtags tailored to each post's content

### **Quality Assurance**
- **JSON Structure Validation**: Ensures proper response format
- **Content Length Optimization**: Platform-appropriate word counts
- **Hashtag Relevance**: Contextual and trending hashtags
- **Engagement Optimization**: Calls-to-action and discussion starters
- **Brand Consistency**: Company context integration when available

---

## 🔒 **Security & Performance**

### **Security Features**
- ✅ **Account Isolation**: Generations scoped to specific accounts
- ✅ **Company Validation**: Ensures company belongs to account before generation
- ✅ **Input Validation**: Query length, platform validation, required fields
- ✅ **Error Handling**: Graceful failures with detailed error messages
- ✅ **Request Logging**: Full request payload stored for debugging and regeneration
- ✅ **API Key Security**: Gemini API key integrated (recommend env variables for production)

### **Performance Considerations**
- ✅ **Async Generation**: Content generation tracked with status updates
- ✅ **Error Recovery**: Failed generations marked with error details and timestamps
- ✅ **Database Indexing**: Optimized queries for account, company, and platform filters
- ✅ **Response Caching**: Consider implementing for frequently requested content
- ✅ **Rate Limiting**: Implement to prevent API abuse and manage costs

### **Data Management**
- **Status Tracking**: `pending` → `completed` / `failed`
- **Request Payload Storage**: Complete request details for regeneration
- **Generated Content Storage**: Full JSON structure with all posts
- **Soft Deletes**: Hard deletes for content generation (no soft delete needed)
- **Timestamp Tracking**: Creation and completion times for analytics

### **Production Recommendations**
- Move Gemini API key to environment variables
- Add rate limiting for content generation (e.g., 10 requests per hour per account)
- Implement content moderation and safety filters
- Add webhook notifications for generation completion
- Monitor AI usage costs and implement quotas
- Consider content approval workflows for enterprise clients
- Add analytics for generation success rates and content performance

---

## 📊 **Analytics & Monitoring**

### **Generation Metrics**
- Total generations per account/company
- Success vs failure rates by platform
- Average generation time by platform
- Most popular content topics and queries
- Platform usage distribution

### **Content Performance**
- Generated posts per platform type
- Content length distribution
- Hashtag usage patterns
- Call-to-action effectiveness (when measurable)

### **System Health**
- API response times
- Gemini API error rates
- Database query performance
- Storage usage for generated content

---

## 📝 **API Summary**

### **Social Media Content Generation Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/social-generate` | Generate AI content for specified platform |
| GET | `/social-generations/{id}` | Get generation by ID with full details |
| GET | `/accounts/{id}/social-generations` | Get all generations for account (filterable) |
| GET | `/companies/{id}/social-generations` | Get all generations for company |
| DELETE | `/social-generations/{id}` | Delete specific generation |
| GET | `/social-platforms` | Get supported platforms with specifications |

### **Supported Platforms & Content Types**
| Platform | Content Type | Optimal Length | Hashtags | Special Features |
|----------|--------------|----------------|-----------|------------------|
| LinkedIn | Professional posts | 150-300 words | 3-5 | Industry insights, thought leadership |
| Instagram | Visual content | 50-150 words | 5-10 | Visual descriptions, story ideas |
| YouTube | Video content | 5-15 minutes | 3-5 | Script outlines, thumbnail suggestions |
| Facebook | Community posts | 80-200 words | 3-7 | Engagement types, audience targeting |
| Blog | Long-form articles | 1500-3000 words | 5-8 | SEO optimization, detailed outlines |

### **Content Generation Features**
- **AI Model**: Gemini 2.0-Flash for high-quality content
- **Uniqueness**: 5 distinct posts per generation, no duplicates
- **Company Context**: Integrates company information when available
- **Error Handling**: Comprehensive validation and recovery
- **Request Storage**: Full payload saved for regeneration capabilities
- **Platform Optimization**: Tailored prompts and formats per platform

---

**Last Updated**: October 7, 2025  
**Version**: 1.0.0  
**AI Model**: Gemini-2.0-Flash  
**API Integration**: Google Generative AI v0.8.2