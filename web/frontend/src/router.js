import { createRouter, createWebHistory } from 'vue-router';
import TaskList from './components/TaskList.vue';
import CreateTaskForm from './components/CreateTaskForm.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: TaskList
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: TaskList
  },
  {
    path: '/create-task',
    name: 'CreateTask',
    component: CreateTaskForm
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;