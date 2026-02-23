<script setup lang="ts">
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { toast } from '@/components/ui/toast'
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import * as z from 'zod'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user.ts'

const router = useRouter()
const userStore = useUserStore()

const formSchema = toTypedSchema(
  z.object({
    name: z.string().min(2, 'Name must have at least 2 characters.').nonempty('Name is required.'),
    email: z.string().email('Please enter a valid email address.').nonempty('Email is required.'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters.')
      .regex(/[A-Z]/, 'Password must include at least one uppercase letter.')
      .regex(/[a-z]/, 'Password must include at least one lowercase letter.')
      .regex(/[0-9]/, 'Password must include at least one number.')
      .nonempty('Password is required.'),
  }),
)

const { handleSubmit } = useForm({
  validationSchema: formSchema,
})

const onSubmit = handleSubmit(async (data) => {
  const result = await userStore.register(data)

  if (result.success) {
    toast({
      title: 'Registration Successful',
      description: result.message || 'Your registration was successful!',
    })
    router.push({ name: 'login' })
  } else {
    toast({
      title: 'Registration Failed',
      description: result.message || 'Please try again.',
    })
  }
})

const redirectToLogin = () => {
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex justify-center items-center min-h-screen-minus-nav bg-gray-100">
    <Card class="w-[500px]">
      <CardHeader>
        <CardTitle>Register</CardTitle>
        <CardDescription>Create your account</CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit="onSubmit" class="space-y-4">
          <FormField name="name" v-slot="{ componentField }">
            <FormItem>
              <FormLabel>
                Name
                <span class="text-red-500 ml-1">*</span>
              </FormLabel>
              <FormControl>
                <Input type="text" placeholder="John" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField name="email" v-slot="{ componentField }">
            <FormItem>
              <FormLabel>
                Email
                <span class="text-red-500 ml-1">*</span>
              </FormLabel>
              <FormControl>
                <Input type="email" placeholder="you@example.com" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField name="password" v-slot="{ componentField }">
            <FormItem>
              <FormLabel>
                Password
                <span class="text-red-500 ml-1">*</span>
              </FormLabel>
              <FormControl>
                <Input type="password" placeholder="Enter your password" v-bind="componentField" />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>
        </form>
      </CardContent>
      <CardFooter class="flex justify-between">
        <Button variant="outline" @click="redirectToLogin"> Login </Button
        ><Button @click="onSubmit"> Register </Button>
      </CardFooter>
    </Card>
  </div>
</template>
