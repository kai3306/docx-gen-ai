import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project } from '../types'

export const useProjectStore = defineStore('project', () => {
  const currentProject = ref<Project | null>(null)

  function setProject(p: Project | null) {
    currentProject.value = p
  }

  return { currentProject, setProject }
})
