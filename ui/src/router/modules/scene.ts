import { hasPermission } from '@/utils/permission/index'
import Layout from '@/layout/main-layout/index.vue'
import { Role } from '@/utils/permission/type'
const sceneRouter = {
  path: '/scene',
  name: 'scene',
  meta: { icon: 'Scene', title: '场景中心', permission: 'SETTING:READ' },
  component: Layout,
  redirect: '/library/aaced38c-1264-11ef-9e86-acde48001122',
  children: [
    {
      path: '/library/aaced38c-1264-11ef-9e86-acde48001122',
      name: 'library',
      meta: {
        icon: 'app-scene-library',
        iconActive: 'app-scene-library-active',
        title: '印象图书',
        activeMenu: '/scene',
        parentPath: '/scene',
        parentName: 'scene',
        permission: new Role('ADMIN')
      },
      component: () => import('@/views/scene/scene-library/index.vue')
    }
  ]
}

export default sceneRouter
