# News Manager - Web Documentation

This directory contains the web documentation for the News Manager project, designed to be hosted on GitHub Pages.

## Structure

- `index.html` - Main page with modern, responsive design and bilingual support
- `_config.yml` - Jekyll configuration for GitHub Pages

## Website Features

### 🌍 Bilingual Support
- **Language Toggle**: Switch between English and Spanish with a click
- **Automatic Detection**: Detects browser language preference
- **Complete Translation**: All content available in both languages
- **SEO Optimized**: Proper language attributes and meta tags

### 🎨 Modern Design
- **Responsive**: Adapts to all devices
- **Gradients**: Attractive design with modern gradients
- **Animations**: Smooth hover effects and transitions
- **Typography**: Readable and professional fonts

### 📱 SEO Optimization
- **Meta tags**: Description, keywords and Open Graph
- **Semantic structure**: HTML5 with semantic elements
- **Performance**: Optimized CSS and fast loading

### 🚀 Featured Content
- **Key features**: 6 cards with core functionalities
- **Quick installation**: Step-by-step commands
- **Usage examples**: 4 practical examples
- **Output demo**: Real example of CLI output
- **Tech stack**: Badges with technologies used

### 🔗 Important Links
- **GitHub**: Direct link to repository
- **Cursor**: Mentions the editor used for development
- **Gemini AI**: Reference to the AI used
- **MIT License**: Link to license

## GitHub Pages Configuration

### 1. Enable GitHub Pages
1. Go to Settings > Pages in the repository
2. Select "Deploy from a branch"
3. Choose the `main` branch and `/docs` folder
4. Save the configuration

### 2. Page URL
The page will be available at:
```
https://fernand0.github.io/news_manager/
```

### 3. Customization
- **Colors**: Modify gradients in CSS
- **Content**: Update HTML as needed
- **Images**: Add logos or project screenshots

## Technologies Used

- **HTML5**: Semantic structure
- **CSS3**: Gradients, flexbox, grid, animations
- **JavaScript**: Language switching functionality
- **Jekyll**: Static site generator (optional)

## Bilingual Features

### Language Switching
- **Toggle Button**: Fixed position in top-right corner
- **Smooth Transitions**: Instant language switching
- **State Management**: Active button highlighting
- **Mobile Responsive**: Adapts to mobile layout

### Content Structure
- **Dual Content**: All sections have both language versions
- **Consistent Layout**: Same design in both languages
- **Proper Attributes**: HTML lang attribute updates
- **Accessibility**: Screen reader friendly

### SEO Benefits
- **Language Detection**: Browser preference detection
- **Meta Tags**: Proper language meta tags
- **Content Duplication**: No duplicate content issues
- **International Reach**: Appeals to global audience

## Development Notes

### Adding New Content
When adding new sections:

1. **Create dual versions**: Add both `.lang-en` and `.lang-es` divs
2. **Maintain structure**: Keep same HTML structure for both
3. **Update JavaScript**: Ensure new content is included in language switching
4. **Test both languages**: Verify content in both English and Spanish

### Translation Guidelines
- **Consistent terminology**: Use same terms across languages
- **Cultural adaptation**: Adapt examples to target audience
- **Technical terms**: Keep technical terms consistent
- **Tone**: Maintain professional tone in both languages

## Future Enhancements

Potential improvements:
- **More languages**: Add support for additional languages
- **Language persistence**: Remember user's language choice
- **Dynamic content**: Load translations dynamically
- **RTL support**: Add support for right-to-left languages 