# MarketMind AI - Android App

Native Android application for market research and marketing campaign management on mobile devices.

---

## 📋 Overview

The Android app provides a native interface for:
- **Market Research**: Chat-based research interface with streaming responses
- **Campaign Results**: Display executed campaign results with success metrics
- **Schedule Management**: Manage scheduled posting times
- **Conversation History**: Track research conversations
- **Offline Support**: Local message caching

**Technology**: Android Native (Java), Firebase, Jetpack components, Markwon markdown rendering

---

## 🏗️ Project Structure

```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/example/marketmindai/
│   │   │   │   ├── activities/
│   │   │   │   │   ├── MainActivity.kt          # Main chat activity
│   │   │   │   │   ├── StrategyActivity.kt      # Strategy view
│   │   │   │   │   └── LoginActivity.kt         # Authentication
│   │   │   │   │
│   │   │   │   ├── adapter/
│   │   │   │   │   ├── ChatAdapter.java         # Chat messages adapter
│   │   │   │   │   └── ConversationAdapter.java # Conversation list
│   │   │   │   │
│   │   │   │   ├── model/
│   │   │   │   │   ├── ChatMessage.java         # Message data model
│   │   │   │   │   ├── StreamMessage.java       # Stream events
│   │   │   │   │   ├── ResearchModels.java      # Research types
│   │   │   │   │   └── User.java                # User model
│   │   │   │   │
│   │   │   │   ├── service/
│   │   │   │   │   ├── ApiService.java          # API client
│   │   │   │   │   ├── AuthService.java         # Authentication
│   │   │   │   │   └── DownloadService.java     # File downloads
│   │   │   │   │
│   │   │   │   ├── util/
│   │   │   │   │   ├── Constants.java           # App constants
│   │   │   │   │   ├── SharedPrefManager.java   # Local storage
│   │   │   │   │   └── Utils.java               # Utilities
│   │   │   │   │
│   │   │   │   └── MyApp.kt                     # App class
│   │   │   │
│   │   │   └── res/
│   │   │       ├── layout/                      # XML layouts
│   │   │       ├── values/                      # Colors, strings, themes
│   │   │       ├── drawable/                    # Images, icons
│   │   │       └── menu/                        # Menu resources
│   │   │
│   │   └── test/                                # Unit tests
│   │
│   ├── google-services.json                     # Firebase config
│   ├── proguard-rules.pro                       # ProGuard rules
│   └── build.gradle.kts
│
├── gradle/
│   └── wrapper/
├── build.gradle.kts                             # Root build config
├── settings.gradle.kts
├── gradle.properties
├── gradlew & gradlew.bat                        # Gradle wrapper
└── README.md
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Android Studio 2023.1+ (Giraffe or later)
- Android SDK 24+ (minimum API level 24)
- Java 11+
- Gradle 8.0+

### 2. Clone & Open Project
```bash
git clone <repository>
cd android
# Open in Android Studio
```

### 3. Configure Firebase

#### Option A: Using Firebase Console
1. Create Firebase project at [firebase.google.com](https://firebase.google.com)
2. Add Android app with bundle ID: `com.example.marketmindai`
3. Download `google-services.json`
4. Place in `app/` directory

#### Option B: Manual Configuration
```json
// app/google-services.json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your_key_id",
  // ... other Firebase config
}
```

### 4. Configure API Endpoint

Edit `util/Constants.java`:
```java
public class Constants {
    public static final String API_BASE_URL = "http://your-backend:5000";
    public static final String DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/...";
}
```

Or use `local.properties`:
```properties
API_BASE_URL=http://10.0.2.2:5000
```

### 5. Build & Run

```bash
# Build
./gradlew build

# Run on connected device/emulator
./gradlew installDebug

# Or from Android Studio
# Click "Run" (Shift + F10) or select "Run > Run 'app'"
```

---

## 📱 Main Features

### 1. Chat Interface (MainActivity)
- Real-time message streaming
- Multiple message types (user, assistant, status, plan, report, strategy, campaign_results)
- Markdown rendering with Markwon
- Auto-scroll to latest message
- Conversation list in sidebar

### 2. Message Types

#### User Message
```java
// Displays right-aligned user input
public class UserMessageVH extends RecyclerView.ViewHolder {
    // User's text message
}
```

#### Assistant Message
```java
// Displays left-aligned LLM response with markdown
public class AssistantMessageVH extends RecyclerView.ViewHolder {
    // Markdown rendering
}
```

#### Campaign Results
```java
// Shows execution results
CampaignLogData {
    campaign_id: String
    results: List<ExecutionResult>  // Backend sends this
    total_briefs: int               // Backend sends this
    total_posted: int               // Backend sends this
}
```

#### Other Types
- `status` - Loading/progress indicators
- `error` - Error messages
- `plan` - Research plan (card format)
- `report` - Market research report
- `strategy` - Marketing strategy
- `content_briefs` - Content briefs for approval
- `stage_b_proposal` - Strategy approval request
- `stage_c_schedule_proposal` - Scheduling interface
- `marketing_form` - Initial marketing form

### 3. Streaming API

```java
// Streaming response handling
val eventSource = client.newWebSocket(request, listener)

override fun onMessage(webSocket: WebSocket, text: String) {
    // Parse NDJSON line
    val event = JSONObject(text)
    when (event.getString("status")) {
        "progress" -> updateProgressUI()
        "plan_completed" -> displayPlan()
        "report_ready" -> displayReport()
        "stage_c_completed" -> displayResults()
    }
}
```

---

## 🔌 API Integration

### ApiService Implementation

```java
public class ApiService {
    private static final String BASE_URL = Constants.API_BASE_URL;
    private final OkHttpClient client;
    
    // Research endpoint
    public void postResearch(JSONObject data, EventListener listener) {
        Request request = new Request.Builder()
            .url(BASE_URL + "/api/research/stage_a")
            .post(RequestBody.create(data.toString(), JSON))
            .addHeader("Authorization", "Bearer " + getToken())
            .build();
        client.newWebSocket(request, listener);
    }
    
    // Strategy endpoint
    public void postStrategy(JSONObject data, Callback callback) {
        Request request = new Request.Builder()
            .url(BASE_URL + "/api/strategy/stage_b")
            .post(RequestBody.create(data.toString(), JSON))
            .build();
        client.newCall(request).enqueue(callback);
    }
}
```

---

## 🔐 Authentication

### Google Sign-In

```java
// In LoginActivity
GoogleSignInOptions gso = new GoogleSignInOptions.Builder()
    .requestIdToken(Constants.GOOGLE_CLIENT_ID)
    .requestEmail()
    .build();

GoogleSignInClient mGoogleSignInClient = GoogleSignIn.getClient(this, gso);

// Handle sign-in result
Task<GoogleSignInAccount> task = GoogleSignIn.getSignedInAccountFromIntent(data);
GoogleSignInAccount account = task.getResult(ApiException.class);
String idToken = account.getIdToken();

// Send token to backend for JWT validation
```

### Token Storage

```java
// SharedPreferences
SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
prefs.edit()
    .putString("jwt_token", jwtToken)
    .putString("user_id", userId)
    .apply();

// Retrieve for API calls
String token = prefs.getString("jwt_token", "");
```

---

## 📲 Data Models

### ChatMessage
```java
public class ChatMessage implements Serializable {
    public String id;
    public String type;  // Message type
    public String content;
    public Date timestamp;
    
    // Nested data classes
    public ClarificationData clarificationData;
    public PlanData planData;
    public ReportData reportData;
    public StrategyData strategyData;
    public CampaignLogData campaignLogData;
    // ... more fields
}
```

### CampaignLogData (Fixed for Backend)
```java
public static class CampaignLogData implements Serializable {
    // Backend fields (primary)
    public String campaign_id;
    public List<ExecutionResult> results;
    public int total_briefs;
    public int total_posted;
    
    // Helper methods for compatibility
    public int getSuccessfulPosts() {
        return total_posted > 0 ? total_posted : successful_posts;
    }
    
    public int getTotalPosts() {
        return total_briefs > 0 ? total_briefs : total_posts;
    }
    
    public List<BriefExecution> getBriefExecutions() {
        // Convert results to briefs_executed format
    }
}
```

### StreamMessage
```java
public class StreamMessage {
    public String status;
    public String message;
    public ChatMessage.CampaignLogData campaign_log;
    public ChatMessage.PlanData plan;
    // ... other fields
}
```

---

## 🎨 UI Components

### ChatAdapter
- `UserMessageVH` - User message display
- `AssistantMessageVH` - LLM response with markdown
- `CardMessageVH` - Plan/Report/Strategy cards
- `ProcessLogVH` - Collapsible process log
- `MarketingFormVH` - Form input
- `ProposalVH` - Strategy approval interface
- `ScheduleProposalVH` - Schedule management

### RecyclerView Setup
```java
RecyclerView chatRecyclerView = findViewById(R.id.rv_chat);
ChatAdapter adapter = new ChatAdapter(messages);
chatRecyclerView.setAdapter(adapter);
chatRecyclerView.setLayoutManager(new LinearLayoutManager(this));

// Add action listener for forms and proposals
adapter.setActionListener(new ChatAdapter.ChatActionListener() {
    @Override
    public void onMarketingFormSubmit(Map<String, Object> formData) {
        postResearchWithFormData(formData);
    }
});
```

---

## 💾 Local Storage

### SharedPreferences
```java
SharedPrefManager prefMgr = new SharedPrefManager(context);

// Save data
prefMgr.saveUserId(userId);
prefMgr.saveAuthToken(token);
prefMgr.saveLastConversation(conversationId);

// Retrieve data
String userId = prefMgr.getUserId();
String token = prefMgr.getAuthToken();
```

### Room Database (Optional)
```java
@Entity(tableName = "messages")
public class MessageEntity {
    @PrimaryKey
    public int id;
    
    public String type;
    public String content;
    public long timestamp;
}
```

---

## 🔄 Message Streaming

### WebSocket Implementation
```java
EventListener eventListener = new EventListener() {
    @Override
    public void onOpen(WebSocket webSocket, Response response) {
        Log.d("Stream", "Connected");
    }
    
    @Override
    public void onMessage(WebSocket webSocket, String text) {
        JSONObject event = new JSONObject(text);
        handleStreamEvent(event);
    }
    
    @Override
    public void onFailure(WebSocket webSocket, Throwable t, Response response) {
        Log.e("Stream", "Error: " + t.getMessage());
    }
};
```

---

## 📊 Campaign Results Display

### Example: Displaying Campaign Results
```java
if ("campaign_results".equals(msg.type) && msg.campaignLogData != null) {
    StringBuilder sb = new StringBuilder("**Kết quả chiến dịch**\n\n");
    
    int successful = msg.campaignLogData.getSuccessfulPosts();
    int total = msg.campaignLogData.getTotalPosts();
    
    sb.append("✅ Thành công: **").append(successful).append("/")
      .append(total).append("** bài đăng\n\n");
    
    // Display brief executions
    List<ChatMessage.BriefExecution> briefs = 
        msg.campaignLogData.getBriefExecutions();
    for (ChatMessage.BriefExecution brief : briefs) {
        String icon = brief.success ? "✅" : "❌";
        sb.append(icon).append(" ").append(brief.title).append("\n");
    }
    
    mw.setMarkdown(tvContent, sb.toString());
}
```

---

## 🚀 Building & Deployment

### Debug Build
```bash
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk
```

### Release Build
```bash
./gradlew assembleRelease
# Output: app/build/outputs/apk/release/app-release.apk
```

### Create Signing Key
```bash
keytool -genkey -v -keystore release.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias release
```

### Sign Release APK
Edit `app/build.gradle.kts`:
```kotlin
signingConfigs {
    release {
        storeFile = file("release.keystore")
        storePassword = "your_password"
        keyAlias = "release"
        keyPassword = "your_password"
    }
}

buildTypes {
    release {
        signingConfig = signingConfigs.release
    }
}
```

---

## 📋 Dependencies

Key dependencies in `build.gradle.kts`:

```gradle
dependencies {
    // AndroidX
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.recyclerview:recyclerview:1.3.0")
    
    // Firebase
    implementation(platform("com.google.firebase:firebase-bom:34.13.0"))
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-auth")
    
    // Google Sign-In
    implementation("com.google.android.gms:play-services-auth:20.7.0")
    
    // OkHttp for networking
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    
    // JSON parsing
    implementation("com.google.code.gson:gson:2.10.1")
    
    // Markdown
    implementation("io.noties.markwon:core:4.6.2")
    
    // Image loading
    implementation("com.squareup.picasso:picasso:2.8")
}
```

---

## 🧪 Testing

### Run Unit Tests
```bash
./gradlew test
```

### Run Instrumented Tests
```bash
./gradlew connectedAndroidTest
```

### Manual Testing Checklist
- [ ] Google Sign-In works
- [ ] API connection successful
- [ ] Chat messages appear
- [ ] Streaming responses update UI
- [ ] Forms submit correctly
- [ ] Campaign results display
- [ ] Campaign results show correct 0/0 → now fixed!

---

## 🆘 Troubleshooting

### "Cannot connect to API"
- Check API endpoint in `Constants.java`
- Ensure backend is running
- Use emulator with proper network setup:
  ```
  10.0.2.2 for localhost on emulator
  actual IP for physical device
  ```

### "Firebase authentication failed"
- Verify `google-services.json` is valid
- Check Firebase project configuration
- Ensure SHA-1 fingerprint matches

### "Markwon rendering not working"
- Check markdown syntax
- Verify Markwon version compatibility
- Ensure TextView is properly initialized

### "Campaign results showing 0/0"
- ✅ Fixed! Update ChatMessage.java with new model structure
- Helper methods now handle both Backend and legacy field names
- See `CampaignLogData.getSuccessfulPosts()` and `getTotalPosts()`

### "Gradle sync failed"
```bash
./gradlew clean
./gradlew sync
```

---

## 📚 Additional Resources

- [Android Developers](https://developer.android.com)
- [Firebase Documentation](https://firebase.google.com/docs)
- [OkHttp Documentation](https://square.github.io/okhttp/)
- [Markwon GitHub](https://github.com/noties/Markwon)
- [Material Design](https://material.io/design)

---

## 🔗 Build Variants

### Debug Configuration
- Logging enabled
- Debuggable
- Fast build

### Release Configuration
- ProGuard enabled
- Signing key required
- Optimized

---

## 📱 Device Requirements

- **Minimum SDK**: API 24 (Android 7.0)
- **Target SDK**: API 34 (Android 14)
- **Recommended**: API 30+

---

**Last Updated**: May 2026
