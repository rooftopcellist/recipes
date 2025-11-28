<nav class="recipe-nav">
  <a href="{{ "/" | relative_url }}">Home</a>
  <a href="{{ "/baking/" | relative_url }}">Baking</a>
  <a href="{{ "/brews/" | relative_url }}">Brews</a>
  <a href="{{ "/cocktails/" | relative_url }}">Cocktails</a>
  <a href="{{ "/desserts/" | relative_url }}">Desserts</a>
  <a href="{{ "/dinner/" | relative_url }}">Dinner</a>
  <a href="{{ "/meal-prep/" | relative_url }}">Meal Prep</a>
  <a href="{{ "/quick-meals/" | relative_url }}">Quick Meals</a>
  <a href="{{ "/sauces/" | relative_url }}">Sauces</a>
  <a href="{{ "/smoothies/" | relative_url }}">Smoothies</a>
  <a href="{{ "/thanksgiving/" | relative_url }}">Thanksgiving</a>
</nav>

<style>
.recipe-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 1rem 0;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e1e4e8;
}

.recipe-nav a {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  text-decoration: none;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.recipe-nav a:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  text-decoration: none;
}
</style>

