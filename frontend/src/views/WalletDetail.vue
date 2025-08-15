<script setup>
import { useRoute, useRouter } from 'vue-router'
import AddressDetail from '@/components/dashboard/AddressDetail.vue'

const route = useRoute()
const router = useRouter()
const address = route.params.address
</script>

<template>
  <div class="p-0">
    <!-- Tampilkan AddressDetail sebagai full-screen drawer -->
    <AddressDetail
      :addressData="{ address }"
      :showModal="true"
      @close="router.back()"
    />
  </div>
</template>