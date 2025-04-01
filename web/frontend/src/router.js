import { createRouter, createWebHistory } from 'vue-router';
import TaskList from './components/TaskList.vue';
import CreateTaskForm from './components/CreateTaskForm.vue';
import DatasetList from './components/DatasetList.vue';
import DatasetDetail from './components/DatasetDetail.vue';

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
  },
  {
    path: '/datasets',
    name: 'Datasets',
    component: DatasetList
  },
  {
    path: '/datasets/:id',
    name: 'DatasetDetail',
    component: DatasetDetail,
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;