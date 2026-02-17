# -Using Vue Router with Vue.js

## Context

We want to use Vue Router because we want to tool for managing client-side navigation in ours Vue.js applications. It enhances the structure , organization, and user experience of your applications by providing a declarative and efficient way to handle routing. 

## Decision 

The decision to use Vue Router is driven by the need for efficient client-side navigation in Vue.js applications, providing a seamless user experience by dynamically loading components, organizing project structure, supporting nested routes, and enabling dynamic routing with route parameters. Vue Router enhances the overall maintainability and responsiveness of the application, making it an ideal choice for building Single Page Applications (SPAs) and leveraging the strengths of the Vue.js framework.

## Rationale

Here some reasons why we need to use Vue Router.

   1. Single Page Application (SPA) Requirement : It can provide a smooth and seamless user experience with client-side navigation. It allows you to create dynamic and interactive SPAs by handling routing on the client side.

   2. Declarative Routing Needs : It can define your application's navigation structure. Declarative routing makes your code more readable and easier to understand, contributing to better maintainability.

   3. Organized Project Structure : It can organized project structure that maps routes to specific components. It encourages the modularization of your code by associating components with specific routes, making it easier to manage and maintain.

## Consequences 
 
If we use vue router, there will be advantages and disadvantages that follow such as:

**Pros** 
   * Efficient Navigation : Vue Router ensures smooth client-side navigation, minimizing full-page reloads for a faster user experience.

   * Declarative Routes : Vue Router's declarative route definition results in cleaner, more readable code for easier maintenance.

   * Route Guards : Vue Router's navigation guards provide a robust mechanism for controlling navigation flow, implementing authentication, authorization, and pre/post-navigation actions.

**Cons**
   * Learning Curve : Beginners may face challenges grasping Vue Router concepts, particularly if new to Vue.js.

   * Configuration Complexity : As projects expand, Vue Router configuration may grow complex, demanding increased maintenance.

   * JavaScript Dependency : Vue Router relies on client-side JavaScript; disabling or encountering errors may disrupt application functionality.

## Sample Code 

1. Create a file **main.js** to set up Vue and Vue Router: 
 
```javascript
    // main.js
    import Vue from 'vue';
    import App from './App.vue';
    import VueRouter from 'vue-router';
    import Home from './components/Home.vue';
    import Product from './components/Product.vue';

    Vue.use(VueRouter);

    const routes = [
    { path: '/', component: Home },
    { path: '/product/:id', component: Product, props: true },
    ];

    const router = new VueRouter({
    routes,
    });

    new Vue({
    render: (h) => h(App),
    router,
    }).$mount('#app');
```
2. Create the main component file **App.vue**:


```html
    <!-- App.vue -->
    <template>
    <div id="app">
        <router-view></router-view>
    </div>
    </template>

    <script>
    export default {
    name: 'App',
    };
    </script>

    <style>
    #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
    }
    </style>
```
3. Create two component files, **Home.vue** and **Product.vue**:

```html 
    <!-- Home.vue -->
    <template>
    <div>
        <h2>Home</h2>
        <router-link to="/product/1">View Product 1</router-link>
    </div>
    </template>

    <script>
    export default {
    name: 'Home',
    };
    </script>
```
```html
    <!-- Product.vue -->
    <template>
    <div>
        <h2>Product {{ productId }}</h2>
        <p>Product details go here.</p>
    </div>
    </template>

    <script>
    export default {
    name: 'Product',
    props: ['id'],
    computed: {
        productId() {
        return this.id;
        },
    },
    };
    </script>
```

4. Create an HTML file (e.g., **index.html**) to load the Vue app:
```html 
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <title>Vue Router Advantages Example</title>
    </head>
    <body>
    <div id="app"></div>
    </body>
    </html>
```