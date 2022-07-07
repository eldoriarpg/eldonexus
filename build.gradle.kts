plugins {
    java
    `maven-publish`
    // make sure to add the eldo nexus as repository in your settings.gradle.kts
    id("de.chojo.publishdata") version "1.0.8"
}

group = "de.eldoria"
version = "1.0.0"

repositories {
    mavenCentral()
    // This repo contains, stable, dev and snapshots
    maven("https://eldonexus.de/repository/maven-public/")
    // This repo contains several common repository proxies.
    maven("https://eldonexus.de/repository/maven-proxies/")
}

dependencies {

}

java{
    // We publish javadocs for our project
    withJavadocJar()
    // We publish sources for our project
    withSourcesJar()

    toolchain{
        // We use java 17 for our builds
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

// configure publish data
publishData {
    // We use the eldo nexus default repositories with "main" as our stable branch
    useEldoNexusRepos(useMain = true)
    // This would use "master" as our stable branch
    // useEldoNexusRepos()

    // We publish everything of the java component, which includes our compiled jar, sources and javadocs
    publishComponent("java")
}

publishing {
    publications.create<MavenPublication>("maven") {
        // Configure our maven publication
        publishData.configurePublication(this)
    }

    repositories {
        // We add EldoNexus as our repository. The used url is defined by the publish data.
        maven {
            authentication {
                credentials(PasswordCredentials::class) {
                    // Those credentials need to be set under "Settings -> Secrets -> Actions" in your repository
                    username = System.getenv("NEXUS_USERNAME")
                    password = System.getenv("NEXUS_PASSWORD")
                }
            }

            name = "EldoNexus"
            setUrl(publishData.getRepository())
        }
    }
}
