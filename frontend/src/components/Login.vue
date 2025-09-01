<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Header -->
      <div class="login-header">
        <div class="logo-section">
          <span class="logo">🍽️</span>
          <h1 class="app-name">BELP</h1>
        </div>
        <p class="tagline">Discover amazing restaurants with AI-powered recommendations</p>
      </div>

      <!-- Tabs -->
      <div class="auth-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'login' }"
          @click="activeTab = 'login'"
        >
          Sign In
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'register' }"
          @click="activeTab = 'register'"
        >
          Create Account
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="login-email" class="form-label">Email</label>
          <input
            id="login-email"
            v-model="loginForm.email"
            type="email"
            class="form-input"
            placeholder="Enter your email"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="login-password" class="form-label">Password</label>
          <div class="password-input-wrapper">
            <input
              id="login-password"
              v-model="loginForm.password"
              :type="showLoginPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showLoginPassword = !showLoginPassword"
            >
              {{ showLoginPassword ? '👁️' : '🙈' }}
            </button>
          </div>
        </div>

        <div class="form-actions">
          <label class="checkbox-wrapper">
            <input type="checkbox" v-model="loginForm.rememberMe" />
            <span class="checkmark"></span>
            Remember me
          </label>
          <a href="#" class="forgot-link">Forgot password?</a>
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          {{ isLoading ? 'Signing In...' : 'Sign In' }}
        </button>

        <div class="demo-note">
          <span class="demo-icon">💡</span>
          <span>Demo: Use any email/password combination</span>
        </div>
      </form>

      <!-- Register Form -->
      <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="register-name" class="form-label">Full Name</label>
          <input
            id="register-name"
            v-model="registerForm.name"
            type="text"
            class="form-input"
            placeholder="Enter your full name"
            required
          />
        </div>

        <div class="form-group">
          <label for="register-username" class="form-label">Username</label>
          <input
            id="register-username"
            v-model="registerForm.username"
            type="text"
            class="form-input"
            placeholder="Choose a username"
            required
          />
        </div>

        <div class="form-group">
          <label for="register-email" class="form-label">Email</label>
          <input
            id="register-email"
            v-model="registerForm.email"
            type="email"
            class="form-input"
            placeholder="Enter your email"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="register-password" class="form-label">Password</label>
          <div class="password-input-wrapper">
            <input
              id="register-password"
              v-model="registerForm.password"
              :type="showRegisterPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="Create a password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showRegisterPassword = !showRegisterPassword"
            >
              {{ showRegisterPassword ? '👁️' : '🙈' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="register-confirm-password" class="form-label">Confirm Password</label>
          <div class="password-input-wrapper">
            <input
              id="register-confirm-password"
              v-model="registerForm.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="Confirm your password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              {{ showConfirmPassword ? '👁️' : '🙈' }}
            </button>
          </div>
        </div>

        <div class="form-actions">
          <label class="checkbox-wrapper">
            <input type="checkbox" v-model="registerForm.agreeToTerms" required />
            <span class="checkmark"></span>
            I agree to the <a href="#" class="terms-link">Terms of Service</a> and <a href="#" class="terms-link">Privacy Policy</a>
          </label>
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          {{ isLoading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <!-- Error/Success Messages -->
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>

      <!-- Social Login -->
      <div class="social-login">
        <div class="divider">
          <span>or continue with</span>
        </div>
        <div class="social-buttons">
          <button class="social-btn google">
            <span class="social-icon">🔍</span>
            Google
          </button>
          <button class="social-btn facebook">
            <span class="social-icon">📘</span>
            Facebook
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import authService from '../services/authService.js'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const activeTab = ref('login')
    const isLoading = ref(false)
    const message = ref('')
    const messageType = ref('')
    
    // Password visibility toggles
    const showLoginPassword = ref(false)
    const showRegisterPassword = ref(false)
    const showConfirmPassword = ref(false)

    // Form data
    const loginForm = reactive({
      email: '',
      password: '',
      rememberMe: false
    })

    const registerForm = reactive({
      name: '',
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false
    })

    // Show message helper
    const showMessage = (text, type = 'info') => {
      message.value = text
      messageType.value = type
      setTimeout(() => {
        message.value = ''
        messageType.value = ''
      }, 5000)
    }

    // Handle login
    const handleLogin = async () => {
      if (!loginForm.email || !loginForm.password) {
        showMessage('Please fill in all fields', 'error')
        return
      }

      isLoading.value = true
      try {
        const result = await authService.login({
          email: loginForm.email,
          password: loginForm.password
        })

        if (result.success) {
          showMessage('Welcome back!', 'success')
          // Redirect to home or profile
          setTimeout(() => {
            router.push('/')
          }, 1000)
        } else {
          showMessage(result.error || 'Login failed', 'error')
        }
      } catch (error) {
        showMessage('An error occurred during login', 'error')
      } finally {
        isLoading.value = false
      }
    }

    // Handle registration
    const handleRegister = async () => {
      if (!registerForm.name || !registerForm.username || !registerForm.email || !registerForm.password) {
        showMessage('Please fill in all fields', 'error')
        return
      }

      if (registerForm.password !== registerForm.confirmPassword) {
        showMessage('Passwords do not match', 'error')
        return
      }

      if (registerForm.password.length < 6) {
        showMessage('Password must be at least 6 characters', 'error')
        return
      }

      if (!registerForm.agreeToTerms) {
        showMessage('Please agree to the terms and conditions', 'error')
        return
      }

      isLoading.value = true
      try {
        const result = await authService.register({
          name: registerForm.name,
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password
        })

        if (result.success) {
          showMessage('Account created successfully!', 'success')
          // Switch to login tab
          setTimeout(() => {
            activeTab.value = 'login'
            loginForm.email = registerForm.email
            // Clear register form
            Object.keys(registerForm).forEach(key => {
              registerForm[key] = key === 'agreeToTerms' ? false : ''
            })
          }, 1000)
        } else {
          showMessage(result.error || 'Registration failed', 'error')
        }
      } catch (error) {
        showMessage('An error occurred during registration', 'error')
      } finally {
        isLoading.value = false
      }
    }

    return {
      activeTab,
      isLoading,
      message,
      messageType,
      showLoginPassword,
      showRegisterPassword,
      showConfirmPassword,
      loginForm,
      registerForm,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  width: 100%;
  max-width: 450px;
  position: relative;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #07450C, #0a5a0f);
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.logo {
  font-size: 2.5rem;
  animation: logoBounce 2s ease-in-out infinite;
}

@keyframes logoBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.app-name {
  font-size: 2rem;
  font-weight: 800;
  color: #07450C;
  margin: 0;
  letter-spacing: 1px;
}

.tagline {
  color: #666;
  font-size: 0.95rem;
  margin: 0;
  line-height: 1.5;
}

/* Tabs */
.auth-tabs {
  display: flex;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 0.25rem;
  margin-bottom: 2rem;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  color: #666;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background: #07450C;
  color: white;
  box-shadow: 0 2px 8px rgba(7, 69, 12, 0.3);
}

.tab-btn:hover:not(.active) {
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
}

/* Form */
.auth-form {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #07450C;
  font-size: 0.9rem;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #07450C;
  box-shadow: 0 0 0 3px rgba(7, 69, 12, 0.1);
}

.form-input::placeholder {
  color: #999;
}

/* Password Input */
.password-input-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.password-toggle:hover {
  background: rgba(7, 69, 12, 0.1);
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
}

.checkbox-wrapper input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid #ddd;
  border-radius: 4px;
  display: inline-block;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark {
  background: #07450C;
  border-color: #07450C;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.forgot-link {
  color: #07450C;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

.terms-link {
  color: #07450C;
  text-decoration: none;
  font-weight: 500;
}

.terms-link:hover {
  text-decoration: underline;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(7, 69, 12, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Loading Spinner */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Demo Note */
.demo-note {
  background: rgba(7, 69, 12, 0.1);
  border: 1px solid rgba(7, 69, 12, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
  margin-top: 1rem;
  text-align: center;
  font-size: 0.85rem;
  color: #07450C;
}

.demo-icon {
  margin-right: 0.5rem;
}

/* Messages */
.message {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: 500;
}

.message.success {
  background: rgba(34, 197, 94, 0.1);
  color: #166534;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.message.error {
  background: rgba(239, 68, 68, 0.1);
  color: #991b1b;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.message.info {
  background: rgba(59, 130, 246, 0.1);
  color: #1e40af;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* Social Login */
.social-login {
  margin-top: 2rem;
}

.divider {
  text-align: center;
  margin-bottom: 1.5rem;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e1e5e9;
}

.divider span {
  background: white;
  padding: 0 1rem;
  color: #666;
  font-size: 0.9rem;
}

.social-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem;
  border: 2px solid #e1e5e9;
  border-radius: 10px;
  background: white;
  color: #333;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.social-btn:hover {
  border-color: #07450C;
  background: rgba(7, 69, 12, 0.05);
}

.social-btn.google:hover {
  border-color: #ea4335;
  background: rgba(234, 67, 53, 0.05);
}

.social-btn.facebook:hover {
  border-color: #1877f2;
  background: rgba(24, 119, 242, 0.05);
}

.social-icon {
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-container {
    padding: 1rem;
  }
  
  .login-card {
    padding: 2rem;
  }
  
  .app-name {
    font-size: 1.75rem;
  }
  
  .logo {
    font-size: 2rem;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .social-buttons {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
  }
  
  .auth-tabs {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .tab-btn {
    border-radius: 6px;
  }
}
</style> 