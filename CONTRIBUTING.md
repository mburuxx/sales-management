# Contributing to Sales Management System

Thank you for your interest in contributing to the Sales Management System! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## 🤝 Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them learn
- **Be collaborative**: Work together towards common goals
- **Be constructive**: Provide helpful feedback and suggestions
- **Be professional**: Maintain a professional atmosphere

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8+ installed
- PostgreSQL database setup
- Git version control
- Basic knowledge of Django framework
- Familiarity with HTML, CSS, and JavaScript

### First Steps

1. **Fork the Repository**
   ```bash
   # Visit GitHub and fork the repository
   # Clone your fork locally
   git clone https://github.com/YOUR_USERNAME/sales-management.git
   cd sales-management
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set Up Database**
   ```bash
   # Navigate to Django project
   cd salesmgt
   
   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   ```

## 🛠 Development Setup

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/feature-name`: Individual feature development
- `bugfix/issue-number`: Bug fixes
- `hotfix/critical-fix`: Critical production fixes

### Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, readable code
   - Follow coding standards
   - Add/update tests
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run tests
   python manage.py test
   
   # Check code style
   flake8 .
   
   # Run coverage
   coverage run manage.py test
   coverage report
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add user authentication feature"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix reported issues
- **Feature enhancements**: Add new functionality
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve test coverage
- **Performance**: Optimize existing code
- **UI/UX**: Improve user interface and experience

### What We're Looking For

- Clean, well-documented code
- Comprehensive test coverage
- User-friendly interfaces
- Performance improvements
- Security enhancements
- Accessibility improvements

### What We're Not Looking For

- Breaking changes without discussion
- Code that doesn't follow our standards
- Features without proper documentation
- Changes without test coverage
- Plagiarized or copyrighted code

## 🔄 Pull Request Process

### Before Submitting

1. **Check Existing Issues**: Look for related issues or discussions
2. **Create Issue**: For major changes, create an issue first
3. **Follow Standards**: Ensure code follows our guidelines
4. **Update Tests**: Add or update relevant tests
5. **Update Documentation**: Document new features or changes

### PR Requirements

- **Clear Description**: Explain what changes were made and why
- **Issue Reference**: Link to related issues
- **Test Coverage**: Include tests for new functionality
- **Documentation**: Update relevant documentation
- **Breaking Changes**: Clearly mark any breaking changes

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainers review the code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR can be merged
5. **Merge**: Maintainers will merge the PR

## 📊 Coding Standards

### Python Code Style

Follow PEP 8 guidelines:

```python
# Good
def calculate_total_price(items, tax_rate=0.1):
    """Calculate total price including tax."""
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax

# Bad
def calc_price(items,tax=0.1):
    """calc total price"""
    total=0
    for item in items:
        total+=item.price
    return total+(total*tax)
```

### Django Best Practices

```python
# Models
class Sale(models.Model):
    """Represents a sale transaction."""
    date_created = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-date_created']
        verbose_name_plural = 'Sales'
    
    def __str__(self):
        return f"Sale #{self.id} - {self.customer.name}"

# Views
class SaleListView(LoginRequiredMixin, ListView):
    """Display list of sales."""
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
```

### HTML/CSS Standards

```html
<!-- Use semantic HTML -->
<article class="sale-card">
    <header class="sale-header">
        <h2 class="sale-title">{{ sale.title }}</h2>
        <time class="sale-date">{{ sale.date_created|date:"M d, Y" }}</time>
    </header>
    <div class="sale-content">
        <!-- Content -->
    </div>
</article>
```

```css
/* Use BEM methodology */
.sale-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
}

.sale-card__header {
    margin-bottom: 12px;
}

.sale-card__title {
    font-size: 1.2rem;
    font-weight: 600;
}
```

### JavaScript Standards

```javascript
// Use modern JavaScript
const calculateTotal = (items, taxRate = 0.1) => {
    const subtotal = items.reduce((sum, item) => sum + item.price, 0);
    const tax = subtotal * taxRate;
    return subtotal + tax;
};

// Use meaningful variable names
const salesData = await fetchSalesData();
const formattedData = formatChartData(salesData);
```

## 🧪 Testing Guidelines

### Test Structure

```python
from django.test import TestCase
from django.contrib.auth.models import User
from sales.models import Sale

class SaleModelTest(TestCase):
    """Test suite for Sale model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.sale = Sale.objects.create(
            customer=self.user,
            total_amount=100.00
        )
    
    def test_sale_creation(self):
        """Test sale is created correctly."""
        self.assertEqual(self.sale.total_amount, 100.00)
        self.assertEqual(str(self.sale), f"Sale #{self.sale.id}")
    
    def test_sale_calculation(self):
        """Test sale total calculation."""
        # Test implementation
        pass
```

### Test Requirements

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Functional Tests**: Test user workflows
- **Coverage**: Aim for >90% test coverage
- **Documentation**: Document test purposes

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test sales

# Run with coverage
coverage run manage.py test
coverage html

# Run specific test class
python manage.py test sales.tests.test_models.SaleModelTest
```

## 📚 Documentation

### Documentation Types

- **README**: Project overview and setup
- **API Documentation**: Endpoint documentation
- **Code Comments**: Inline documentation
- **User Guide**: End-user documentation
- **Developer Guide**: Technical documentation

### Documentation Standards

```python
def process_sale(customer_id, items, discount=0.0):
    """
    Process a new sale transaction.
    
    Args:
        customer_id (int): ID of the customer making the purchase
        items (list): List of items being purchased
        discount (float, optional): Discount percentage. Defaults to 0.0.
    
    Returns:
        Sale: The created sale object
    
    Raises:
        ValidationError: If customer doesn't exist or items are invalid
        
    Example:
        >>> items = [{'id': 1, 'quantity': 2}, {'id': 2, 'quantity': 1}]
        >>> sale = process_sale(customer_id=123, items=items, discount=0.1)
        >>> print(sale.total_amount)
        90.00
    """
    # Implementation
```

### Updating Documentation

- Update README for new features
- Add docstrings to new functions/classes
- Update API documentation for endpoint changes
- Add examples for complex functionality

## 🐛 Issue Reporting

### Before Reporting

1. **Search Existing Issues**: Check if issue already exists
2. **Update Dependencies**: Ensure you're using latest version
3. **Reproduce**: Verify the issue is reproducible
4. **Gather Information**: Collect relevant details

### Bug Report Template

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- Django Version: [e.g., 4.2.7]
- Browser: [e.g., Chrome 91.0]

**Additional Context**
Any other context about the problem.
```

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
Describe your proposed solution.

**Alternatives Considered**
Alternative solutions you've considered.

**Additional Context**
Any other context or screenshots about the feature.
```

## 🏆 Recognition

Contributors will be recognized in the following ways:

- **Contributors List**: Added to project contributors
- **Release Notes**: Mentioned in release announcements
- **Hall of Fame**: Featured in project documentation
- **Maintainer Invitation**: Outstanding contributors may be invited as maintainers

## 📞 Getting Help

If you need help or have questions:

- **GitHub Issues**: Create an issue for bugs or features
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check existing documentation
- **Code Comments**: Review inline documentation

## 🔄 Development Lifecycle

### Regular Contributor Path

1. **Start Small**: Begin with documentation or small bug fixes
2. **Learn Codebase**: Understand project structure and patterns
3. **Take on Features**: Implement new features or enhancements
4. **Review Code**: Help review other contributors' PRs
5. **Mentor Others**: Help new contributors get started

### Maintainer Path

Outstanding contributors may be invited to become maintainers with additional responsibilities:

- Code review and PR approval
- Issue triage and management
- Release planning and coordination
- Community management and support

---

Thank you for contributing to the Sales Management System! Your contributions help make this project better for everyone. 🎉