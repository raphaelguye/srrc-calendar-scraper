# SRRC Calendar Scraper Migration Guide

## From Python + GitHub Releases → Kotlin + Spring Boot + Railway

This document outlines the step-by-step migration from the current Python scraper with GitHub Releases to a full Kotlin Spring Boot API deployed on Railway.

---

## 📋 Migration Overview

### Current State (Phase 1)
- ✅ Python scraper (`srrc_event_scraper.py`)
- ✅ GitHub Actions for scheduled scraping
- ✅ GitHub Releases for data distribution
- ✅ Mobile app consumes GitHub Releases API

### Target State (Phase 2)
- 🎯 Kotlin scraper + Spring Boot API
- 🎯 Railway cloud deployment
- 🎯 RESTful API endpoints
- 🎯 Mobile app consumes Railway API

---

## 🚀 Phase 1: Setup Current Python + GitHub Releases (Simple Solution)

### Step 1.1: Create GitHub Actions Workflow

Create `.github/workflows/scraper.yml`:

```yaml
name: SRRC Event Scraper

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4
      
      - name: Run scraper
        run: python3 srrc_event_scraper.py
      
      - name: Create timestamp
        id: timestamp
        run: echo "timestamp=$(date +'%Y-%m-%d_%H-%M-%S')" >> $GITHUB_OUTPUT
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: data-${{ steps.timestamp.outputs.timestamp }}
          name: Events Data ${{ steps.timestamp.outputs.timestamp }}
          files: srrc_events.json
          body: |
            🤖 Automated scrape of SRRC events
            📊 Generated: ${{ steps.timestamp.outputs.timestamp }}
            🔄 Run: ${{ github.run_number }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 1.2: Test Mobile App Integration

Flutter/Dart example:
```dart
class EventService {
  static const String repoUrl = 'https://api.github.com/repos/YOUR_USERNAME/srrc-calendar-scraper/releases/latest';
  
  Future<List<Event>> fetchLatestEvents() async {
    // Get latest release info
    final releaseResponse = await http.get(Uri.parse(repoUrl));
    final release = json.decode(releaseResponse.body);
    
    // Find the JSON asset
    final asset = release['assets'].firstWhere(
      (asset) => asset['name'] == 'srrc_events.json'
    );
    
    // Download the actual events
    final eventsResponse = await http.get(Uri.parse(asset['browser_download_url']));
    final eventsJson = json.decode(eventsResponse.body);
    
    return eventsJson.map<Event>((json) => Event.fromJson(json)).toList();
  }
}
```

### Step 1.3: Validation Checklist

- [ ] GitHub Actions runs successfully
- [ ] Releases are created with JSON files
- [ ] Mobile app can fetch and parse events
- [ ] Scheduled runs work as expected

---

## 🔄 Phase 2: Migration to Kotlin + Spring Boot + Railway

### Step 2.1: Project Setup

#### 2.1.1: Initialize Gradle Project

```bash
# Create project structure
mkdir -p src/main/kotlin/com/srrc/scraper
mkdir -p src/main/resources
mkdir -p src/test/kotlin

# Create Gradle wrapper
gradle wrapper --gradle-version 8.4
```

#### 2.1.2: Create `build.gradle.kts`

```kotlin
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
    kotlin("jvm") version "1.9.20"
    kotlin("plugin.spring") version "1.9.20"
    application
}

group = "com.srrc"
version = "1.0.0"

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    
    // HTTP Client & HTML Parsing
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jsoup:jsoup:1.17.1")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // Testing
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

application {
    mainClass.set("com.srrc.scraper.SRRCEventScraperKt")
}

tasks.register<JavaExec>("runScraper") {
    group = "application"
    description = "Run the SRRC event scraper"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.srrc.scraper.SRRCEventScraperKt")
}

tasks.named<org.springframework.boot.gradle.tasks.bundling.BootJar>("bootJar") {
    archiveFileName.set("srrc-api.jar")
    mainClass.set("com.srrc.scraper.SrrcApiApplicationKt")
}

tasks.withType<KotlinCompile> {
    kotlinOptions {
        freeCompilerArgs += "-Xjsr305=strict"
        jvmTarget = "17"
    }
}
```

### Step 2.2: Convert Python Scraper to Kotlin

#### 2.2.1: Create Data Models

`src/main/kotlin/com/srrc/scraper/Event.kt`:
```kotlin
package com.srrc.scraper

import com.fasterxml.jackson.annotation.JsonProperty

data class Event(
    @JsonProperty("date_display") val dateDisplay: String = "",
    val month: String = "",
    val weekday: String = "",
    val title: String = "",
    val url: String = "",
    @JsonProperty("event_id") val eventId: String = "",
    val location: String = "",
    @JsonProperty("start_date") val startDate: String = "",
    @JsonProperty("end_date") val endDate: String = "",
    val description: String = "",
    val organizer: String = ""
)

data class AjaxResponse(
    @JsonProperty("has_more_event") val hasMoreEvent: Int = 0,
    val html: String = "",
    val count: Int = 0
)
```

#### 2.2.2: Create Kotlin Scraper

`src/main/kotlin/com/srrc/scraper/SRRCEventScraper.kt`:
```kotlin
package com.srrc.scraper

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import kotlinx.coroutines.*
import okhttp3.*
import org.jsoup.Jsoup
import java.io.File
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.concurrent.TimeUnit

class SRRCEventScraper {
    private val baseUrl = "https://srrc.ch/wp-admin/admin-ajax.php"
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .build()
    private val mapper = jacksonObjectMapper()
    
    suspend fun fetchAllEvents(): List<Event> {
        // Implementation here (refer to previous Kotlin code)
        // This converts the Python logic to Kotlin
    }
    
    // Other methods...
}

suspend fun main() {
    println("🚀 SRRC Kotlin Scraper Starting...")
    
    val scraper = SRRCEventScraper()
    val events = scraper.fetchAllEvents()
    
    println("📊 Found ${events.size} unique events")
    
    val mapper = jacksonObjectMapper()
    File("srrc_events.json").writeText(
        mapper.writerWithDefaultPrettyPrinter().writeValueAsString(events)
    )
    
    println("✅ Events saved to srrc_events.json")
}
```

### Step 2.3: Create Spring Boot API

#### 2.3.1: Main Application Class

`src/main/kotlin/com/srrc/scraper/SrrcApiApplication.kt`:
```kotlin
package com.srrc.scraper

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class SrrcApiApplication

fun main(args: Array<String>) {
    runApplication<SrrcApiApplication>(*args)
}
```

#### 2.3.2: REST Controller

`src/main/kotlin/com/srrc/scraper/EventController.kt`:
```kotlin
package com.srrc.scraper

import org.springframework.web.bind.annotation.*
import org.springframework.stereotype.Service
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import java.io.File
import java.time.LocalDateTime

@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = ["*"])
class EventController(private val eventService: EventService) {
    
    @GetMapping("/events")
    fun getAllEvents(): ApiResponse<List<Event>> {
        return ApiResponse.success(eventService.getAllEvents())
    }
    
    @GetMapping("/events/upcoming")
    fun getUpcomingEvents(@RequestParam(defaultValue = "10") limit: Int): ApiResponse<List<Event>> {
        return ApiResponse.success(eventService.getUpcomingEvents(limit))
    }
    
    @GetMapping("/events/search")
    fun searchEvents(@RequestParam query: String): ApiResponse<List<Event>> {
        return ApiResponse.success(eventService.searchEvents(query))
    }
    
    @GetMapping("/status")
    fun getStatus(): ApiResponse<Map<String, Any>> {
        return ApiResponse.success(eventService.getStatus())
    }
}

@Service
class EventService {
    // Service implementation
}

data class ApiResponse<T>(
    val success: Boolean,
    val data: T? = null,
    val error: String? = null,
    val timestamp: String = LocalDateTime.now().toString()
) {
    companion object {
        fun <T> success(data: T) = ApiResponse(success = true, data = data)
        fun <T> error(message: String) = ApiResponse<T>(success = false, error = message)
    }
}
```

### Step 2.4: Update GitHub Actions

`.github/workflows/kotlin-scraper.yml`:
```yaml
name: Kotlin SRRC Scraper & Deploy

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Cache Gradle packages
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}
      
      - name: Make gradlew executable
        run: chmod +x ./gradlew
      
      - name: Build JAR
        run: ./gradlew bootJar
      
      - name: Run scraper
        run: ./gradlew runScraper
      
      - name: Deploy to Railway
        uses: railwayapp/railway-deploy@v3
        with:
          service: srrc-api
          environment: production
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Step 2.5: Railway Deployment Setup

#### 2.5.1: Create Railway Account & Project
1. Go to [railway.app](https://railway.app)
2. Connect GitHub account
3. Create new project from GitHub repo
4. Railway auto-detects Spring Boot

#### 2.5.2: Configure Railway

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "java -jar build/libs/srrc-api.jar",
    "healthcheckPath": "/api/v1/status"
  }
}
```

#### 2.5.3: Environment Variables
In Railway dashboard, set:
```
PORT=8080
SPRING_PROFILES_ACTIVE=production
```

### Step 2.6: Update Mobile App

Change from GitHub Releases API to Railway API:

```dart
class EventService {
  static const String apiUrl = 'https://your-app.railway.app/api/v1';
  
  Future<List<Event>> fetchLatestEvents() async {
    final response = await http.get(Uri.parse('$apiUrl/events/upcoming'));
    final apiResponse = json.decode(response.body);
    
    if (apiResponse['success']) {
      return (apiResponse['data'] as List)
          .map((json) => Event.fromJson(json))
          .toList();
    } else {
      throw Exception(apiResponse['error']);
    }
  }
  
  Future<List<Event>> searchEvents(String query) async {
    final response = await http.get(
      Uri.parse('$apiUrl/events/search?query=$query')
    );
    final apiResponse = json.decode(response.body);
    return (apiResponse['data'] as List)
        .map((json) => Event.fromJson(json))
        .toList();
  }
}
```

---

## 🧪 Testing & Validation

### Phase 1 Testing
```bash
# Test Python scraper locally
python3 srrc_event_scraper.py

# Test GitHub Actions (manual trigger)
# Go to GitHub Actions tab and click "Run workflow"

# Test mobile app with GitHub Releases API
```

### Phase 2 Testing
```bash
# Test Kotlin scraper
./gradlew runScraper

# Test Spring Boot API locally
./gradlew bootRun
# Visit: http://localhost:8080/api/v1/events

# Test Railway deployment
# Visit: https://your-app.railway.app/api/v1/status
```

---

## 📊 Benefits Comparison

| Aspect | Phase 1 (Python + GitHub) | Phase 2 (Kotlin + Railway) |
|--------|---------------------------|----------------------------|
| **Complexity** | ⭐⭐ Simple | ⭐⭐⭐⭐ Advanced |
| **Cost** | 🆓 Free | 💰 ~$5/month |
| **Performance** | ⚡ Good | ⚡⚡⚡ Excellent |
| **Scalability** | 📈 Limited | 📈📈📈 High |
| **API Features** | 🔧 Basic | 🔧🔧🔧 Rich |
| **Mobile Integration** | 📱 GitHub API | 📱📱 Native REST |
| **Learning Value** | 🎓 Moderate | 🎓🎓🎓 High |

---

## 🗂️ File Structure Comparison

### Phase 1 Structure
```
srrc-calendar-scraper/
├── srrc_event_scraper.py
├── requirements.txt
├── .github/workflows/scraper.yml
├── README.md
└── srrc_events.json (generated)
```

### Phase 2 Structure
```
srrc-calendar-scraper/
├── src/main/kotlin/com/srrc/scraper/
│   ├── SRRCEventScraper.kt
│   ├── SrrcApiApplication.kt
│   ├── EventController.kt
│   └── Event.kt
├── build.gradle.kts
├── gradlew
├── railway.json
├── .github/workflows/kotlin-scraper.yml
├── MIGRATION_GUIDE.md
└── build/libs/srrc-api.jar (generated)
```

---

## ⚠️ Migration Risks & Mitigation

### Risks
1. **Kotlin learning curve** → Start with scraper only, add API later
2. **Railway costs** → Monitor usage, use free tier initially
3. **Breaking mobile app** → Keep Phase 1 running during transition
4. **Data format changes** → Maintain JSON compatibility

### Mitigation Strategy
1. **Parallel development** → Build Phase 2 alongside Phase 1
2. **Feature flags** → Toggle between GitHub/Railway APIs
3. **Gradual migration** → Mobile app supports both APIs
4. **Rollback plan** → Keep Phase 1 workflows ready

---

## 🎯 Recommended Timeline

### Week 1-2: Phase 1 Implementation
- [ ] Set up GitHub Actions
- [ ] Test Python scraper automation
- [ ] Validate mobile app integration

### Week 3-4: Kotlin Learning
- [ ] Convert scraper to Kotlin
- [ ] Test Kotlin scraper locally
- [ ] Compare output with Python version

### Week 5-6: Spring Boot API
- [ ] Create REST endpoints
- [ ] Test API locally
- [ ] Design mobile app integration

### Week 7-8: Railway Deployment
- [ ] Set up Railway account
- [ ] Deploy and test
- [ ] Update mobile app
- [ ] Monitor and optimize

---

## 📞 Support & Resources

### Documentation
- [Spring Boot Reference](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Railway Documentation](https://docs.railway.app/)
- [OkHttp Documentation](https://square.github.io/okhttp/)

### Troubleshooting
- GitHub Actions logs for debugging
- Railway deployment logs
- Spring Boot actuator endpoints
- Mobile app network debugging

---

## ✅ Final Checklist

### Phase 1 Completion
- [ ] Python scraper runs in GitHub Actions
- [ ] Releases created successfully
- [ ] Mobile app consumes GitHub API
- [ ] Scheduled scraping works

### Phase 2 Completion
- [ ] Kotlin scraper produces same data
- [ ] Spring Boot API responds correctly
- [ ] Railway deployment successful
- [ ] Mobile app uses new API
- [ ] Old GitHub Actions disabled

---

*Generated on November 7, 2025*
*This guide assumes basic knowledge of Git, GitHub, and mobile app development*