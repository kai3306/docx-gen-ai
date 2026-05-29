import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('../components/AppLayout.vue'),
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
        { path: 'projects', name: 'ProjectList', component: () => import('../views/ProjectList.vue') },
        { path: 'projects/:id', name: 'ProjectDetail', component: () => import('../views/ProjectDetail.vue') },
        { path: 'upload', name: 'Upload', component: () => import('../views/Upload.vue') },
        { path: 'ai-generate', name: 'AiGenerate', component: () => import('../views/AiGenerate.vue') },
        { path: 'documents', name: 'DocumentList', component: () => import('../views/DocumentList.vue') },
        { path: 'form-templates', name: 'FormTemplateList', component: () => import('../views/FormTemplateList.vue') },
        { path: 'form-templates/edit/:id?', name: 'FormTemplateEdit', component: () => import('../views/FormTemplateEdit.vue') },
        { path: 'form-fill', name: 'FormFill', component: () => import('../views/FormFill.vue') },
        { path: 'template-groups', name: 'TemplateGroupList', component: () => import('../views/TemplateGroupList.vue') },
        { path: 'template-groups/:id', name: 'TemplateGroupDetail', component: () => import('../views/TemplateGroupDetail.vue') },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
