<template>
  <div class="home-container">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          Discover Your Perfect
          <span class="highlight">Restaurant</span>
        </h1>
        <p class="hero-subtitle">
          Powered by AI and real user reviews. Find restaurants that match your taste, 
          dietary needs, and mood. From hidden gems to popular favorites.
        </p>
        <div class="hero-actions">
          <router-link to="/search" class="cta-btn primary">
            <span class="btn-icon">🔍</span>
            Start Exploring
          </router-link>
          <router-link to="/share" class="cta-btn secondary">
            <span class="btn-icon">📤</span>
            Share Your Finds
          </router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-card card-1">
          <span class="card-emoji">🍕</span>
          <span class="card-text">Best Pizza</span>
        </div>
        <div class="floating-card card-2">
          <span class="card-emoji">🍜</span>
          <span class="card-text">Fresh Ramen</span>
        </div>
        <div class="floating-card card-3">
          <span class="card-emoji">🌮</span>
          <span class="card-text">Taco Tuesday</span>
        </div>
        <div class="floating-card card-4">
          <span class="card-emoji">🍣</span>
          <span class="card-text">Sushi Master</span>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h2 class="section-title">Why Choose BELP?</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3 class="feature-title">AI-Powered</h3>
          <p class="feature-description">
            Advanced machine learning algorithms analyze reviews, ratings, and preferences 
            to give you personalized restaurant recommendations.
          </p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3 class="feature-title">Personalized</h3>
          <p class="feature-description">
            Get recommendations based on your dietary restrictions, favorite cuisines, 
            and dining preferences.
          </p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">👥</div>
          <h3 class="feature-title">Community-Driven</h3>
          <p class="feature-description">
            Discover restaurants through friends, food bloggers, and the community. 
            Share your own discoveries and build lists.
          </p>
        </div>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="how-it-works-section">
      <h2 class="section-title">How It Works</h2>
      <div class="steps-container">
        <div class="step-item">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3 class="step-title">Tell Us What You Want</h3>
            <p class="step-description">
              Share your cravings, dietary needs, or just browse by location. 
              Our AI understands natural language.
            </p>
          </div>
        </div>
        <div class="step-item">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3 class="step-title">Get Smart Recommendations</h3>
            <p class="step-description">
              We analyze thousands of reviews and ratings to find restaurants 
              that match your preferences perfectly.
            </p>
          </div>
        </div>
        <div class="step-item">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3 class="step-title">Discover & Share</h3>
            <p class="step-description">
              Visit amazing restaurants and share your experiences with the community. 
              Help others discover great places too!
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-number">50K+</div>
          <div class="stat-label">Restaurants</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">1M+</div>
          <div class="stat-label">Reviews</div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="cta-section">
      <h2 class="cta-title">Ready to Find Your Next Favorite Restaurant?</h2>
      <p class="cta-subtitle">
        Join thousands of food lovers who are already discovering amazing places to eat.
      </p>
      <div class="cta-actions">
        <router-link to="/search" class="cta-btn primary large">
          <span class="btn-icon">🚀</span>
          Get Started Now
        </router-link>
        <router-link to="/profile" class="cta-btn secondary large">
          <span class="btn-icon">👤</span>
          Create Profile
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Hero Section */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  min-height: 80vh;
  padding: 4rem 0;
}

.hero-content {
  z-index: 2;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: bold;
  color: #07450C;
  margin: 0 0 1.5rem 0;
  line-height: 1.2;
}

.highlight {
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: #07450C;
  margin: 0 0 2rem 0;
  line-height: 1.6;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.cta-btn.primary {
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  box-shadow: 0 4px 15px rgba(7, 69, 12, 0.3);
}

.cta-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(7, 69, 12, 0.4);
}

.cta-btn.secondary {
  background: white;
  color: #07450C;
  border-color: #07450C;
}

.cta-btn.secondary:hover {
  background: #07450C;
  color: white;
}

.cta-btn.large {
  padding: 1.25rem 2.5rem;
  font-size: 1.2rem;
}

.btn-icon {
  font-size: 1.2rem;
}

/* Hero Visual */
.hero-visual {
  position: relative;
  height: 400px;
}

.floating-card {
  position: absolute;
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 2px solid rgba(7, 69, 12, 0.1);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  animation: float 6s ease-in-out infinite;
}

.floating-card.card-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.floating-card.card-2 {
  top: 40%;
  right: 20%;
  animation-delay: 1s;
}

.floating-card.card-3 {
  bottom: 30%;
  left: 20%;
  animation-delay: 2s;
}

.floating-card.card-4 {
  bottom: 20%;
  right: 10%;
  animation-delay: 3s;
}

.card-emoji {
  font-size: 1.5rem;
}

.card-text {
  color: #07450C;
  font-weight: bold;
  font-size: 0.9rem;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

/* Features Section */
.features-section {
  padding: 4rem 0;
  text-align: center;
}

.section-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #07450C;
  margin: 0 0 3rem 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(7, 69, 12, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-title {
  font-size: 1.3rem;
  font-weight: bold;
  color: #07450C;
  margin: 0 0 1rem 0;
}

.feature-description {
  color: #07450C;
  line-height: 1.6;
  opacity: 0.8;
}

/* How It Works Section */
.how-it-works-section {
  padding: 4rem 0;
  background: linear-gradient(135deg, rgba(7, 69, 12, 0.03), rgba(7, 69, 12, 0.08));
  margin: 2rem -2rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.steps-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.step-number {
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  flex-shrink: 0;
}

.step-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #07450C;
  margin: 0 0 0.5rem 0;
}

.step-description {
  color: #07450C;
  line-height: 1.6;
  opacity: 0.8;
}

/* Stats Section */
.stats-section {
  padding: 4rem 0;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-item {
  padding: 2rem;
}

.stat-number {
  font-size: 3rem;
  font-weight: bold;
  color: #07450C;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #07450C;
  font-size: 1.1rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* CTA Section */
.cta-section {
  padding: 4rem 0;
  text-align: center;
  background: linear-gradient(135deg, rgba(7, 69, 12, 0.05), rgba(7, 69, 12, 0.1));
  margin: 2rem -2rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #07450C;
  margin: 0 0 1rem 0;
}

.cta-subtitle {
  font-size: 1.2rem;
  color: #07450C;
  margin: 0 0 2rem 0;
  opacity: 0.8;
}

.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 2rem;
  }
  
  .hero-visual {
    height: 300px;
  }
  
  .floating-card {
    transform: scale(0.8);
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 0 1rem;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .cta-btn {
    padding: 0.875rem 1.75rem;
    font-size: 1rem;
  }
  
  .cta-btn.large {
    padding: 1rem 2rem;
    font-size: 1.1rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .steps-container {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .cta-title {
    font-size: 2rem;
  }
  
  .cta-actions {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 2rem 0;
    min-height: 60vh;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .floating-card {
    transform: scale(0.7);
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-card {
    padding: 1.5rem;
  }
  
  .step-item {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
}
</style> 