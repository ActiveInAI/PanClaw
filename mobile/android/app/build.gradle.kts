plugins {
    id("com.android.application")
}

android {
    namespace = "ai.active.panclaw"
    compileSdk = 35

    defaultConfig {
        applicationId = "ai.active.panclaw"
        minSdk = 26
        targetSdk = 35
        versionCode = 8
        versionName = "0.5.1"
    }
}
