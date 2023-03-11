import { ref, computed, reactive } from 'vue'
import type { Ref } from 'vue'
import { defineStore } from 'pinia'
import { USER_TYPE } from '@/assets/js/login'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }

  return { count, doubleCount, increment }
})

export enum USER_STATUS {
    k_noinit,
    k_nologin,
    k_logined,
    k_entering,
};

export const UserInfo = defineStore('UserInfo', () => {
  const user_ip:Ref<string> = ref("127.0.0.1")
  const user_name:Ref<string> = ref("未登陆")
  const user_status:Ref<USER_STATUS> = ref(USER_STATUS.k_nologin)
  const user_group:Ref<string> = ref("默认组")
  const user_lv:Ref<USER_TYPE> = ref(USER_TYPE.normalize)
  return { user_ip, user_name, user_status, user_group, user_lv }
})
