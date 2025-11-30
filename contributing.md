# Contribute your Recipes!

## Open a Pull Request

### Recipe structure

Recipes are written in Markdown, then Github Pages uses Jekyll to render this Markdown so that these static files can be hosted.  The are hosted at https://rooftopcellist.github.io/recipes

Typically, a recipe will have the following structure:
* Category: Which category this falls under (dinner, breakfast, "new category", etc.)
* Recipe Name
* Teaser Picture: Pictures to include at the top of the recipe
* Ingredients: list of ingredients, each on a new line. For example: "1 tsp Salt (sprinkled on top)"
* Cooking Instructions: list of actions to take to cook ze delicious food
* Tips/Pairings/Note to chef
* Final Picture (s): Pictures to include in the recipe page. Please limit this to one picture per recipe, and reduce the resolution to medium. The image format should be .jpeg or .png

Here is a [sample recipe](./samples/sample-recipe.md) to show you what I mean. 

After you create a pull request, it will be reviewed and merged by on of the maintainers.  

### Add recipe via form

The easiest way to contribute a recipe is by filling out our Google Form:

**[Submit a Recipe](https://forms.gle/GwuBYMKoseXQhZeu8)**

Once a week, recipe submissions will be reviewed and added to the site.

**Note:** When filling out the ingredients and instructions, please use line breaks to make it easier to read. Each new line will be shown as a bullet point in a list when it is published on the website.

### Add recipe via code contribution

1. Clone the repo (fork it if you haven't already)
2. Add a new file in the directory with the name of the category your recipe falls under
3. Add recipe contents in Markdown format.  Note: be sure not to use HTML specifc tags as this will cause issues when Jekyll renders the page.  
4. Add a link to that file in the README.md inside that directory (for example: ./dinner/README.md)
5. Push your changes to your fork, then open a pull request and request a review.  
