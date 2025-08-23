# BELP Frontend

A modern, responsive restaurant recommendation application built with Vue.js 3 and Vite.

## Features

### 🏠 Home Page
- **Hero Section**: Engaging landing page with animated floating restaurant cards
- **Features Overview**: Highlights AI-powered recommendations, personalization, and community features
- **How It Works**: Step-by-step guide for users
- **Statistics**: Impressive numbers to build trust
- **Call-to-Action**: Clear paths to get started

### 🔍 Search Interface
- **Advanced Filters**: Dietary restrictions, ambiance, price range, and minimum rating
- **Location Search**: Find restaurants by city, state, or zip code
- **Craving Search**: Natural language search for specific food types or occasions
- **Smart Results**: AI-powered restaurant recommendations with detailed information
- **Sorting Options**: Sort by rating, popularity, or best match
- **Infinite Scroll**: Load more results as you scroll

### 👤 Profile Page
- **User Dashboard**: Overview of activity and preferences
- **Dietary Preferences**: Manage vegetarian, vegan, gluten-free, and other dietary needs
- **Favorite Cuisines**: Interactive cuisine selection with toggle functionality
- **Review History**: Track and display recent restaurant reviews
- **Favorite Restaurants**: Manage and organize favorite dining spots
- **Account Settings**: Update profile information and preferences

### 📤 Share Page
- **Quick Share**: Easy restaurant sharing with ratings and descriptions
- **List Creation**: Build and organize restaurant lists with privacy controls
- **Social Feed**: Discover recommendations from friends and community
- **Trending Topics**: Join popular food trends and discussions
- **Privacy Controls**: Public, friends-only, or private sharing options

## Technical Features

### 🎨 Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Touch-Friendly**: Mobile-optimized interactions
- **Progressive Enhancement**: Works on all devices
- **Accessibility**: ARIA labels and keyboard navigation support

### 🚀 Performance
- **Vue 3 Composition API**: Modern reactive system
- **Vite Build Tool**: Fast development and optimized builds
- **Lazy Loading**: Components loaded on demand
- **Optimized Assets**: Efficient image and icon usage

### 🔧 Development
- **Component-Based**: Modular, reusable components
- **Vue Router**: Client-side routing with navigation guards
- **State Management**: Reactive data management
- **CSS Grid & Flexbox**: Modern layout techniques

## Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Preview
```bash
npm run preview
```

## Project Structure

```
src/
├── components/          # Reusable Vue components
│   ├── Home.vue        # Landing page component
│   └── YelpSearch.vue  # Search and results component
├── views/              # Page components
│   ├── Profile.vue     # User profile page
│   └── Share.vue       # Social sharing page
├── router/             # Vue Router configuration
├── assets/             # Static assets
└── main.js            # Application entry point
```

## Design System

### Colors
- **Primary**: #07450C (Dark Green)
- **Secondary**: #0a5a0f (Lighter Green)
- **Accent**: #FFD700 (Gold for ratings)
- **Background**: White with subtle gradients
- **Text**: #07450C with opacity variations

### Typography
- **Headings**: Bold, scalable font sizes
- **Body**: Readable line heights and spacing
- **Interactive**: Clear hover and focus states

### Components
- **Cards**: Consistent spacing and shadows
- **Buttons**: Gradient backgrounds with hover effects
- **Forms**: Clean inputs with focus states
- **Navigation**: Sticky header with mobile menu

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility

- **Semantic HTML**: Proper heading hierarchy
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: WCAG AA compliant
- **Focus Management**: Clear focus indicators

## Future Enhancements

- [ ] User authentication system
- [ ] Real-time notifications
- [ ] Advanced filtering algorithms
- [ ] Social media integration
- [ ] Mobile app development
- [ ] Offline support
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Advanced analytics
- [ ] A/B testing framework

