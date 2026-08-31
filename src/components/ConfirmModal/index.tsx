import React from 'react'
import { View, Text, Button } from '@tarojs/components'
import './index.scss'

interface ConfirmModalProps {
  isOpen: boolean
  title: string
  content: string
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmModal({
  isOpen,
  title,
  content,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel
}: ConfirmModalProps) {
  if (!isOpen) return null

  return (
    <View className="modal-overlay">
      <View className="modal-card">
        <View className="modal-header">
          <Text className="modal-title">{title}</Text>
          <Text className="modal-content">{content}</Text>
        </View>
        <Button className="btn-confirm" onClick={onConfirm}>
          {confirmText}
        </Button>
        <Button className="btn-cancel" onClick={onCancel}>
          {cancelText}
        </Button>
      </View>
    </View>
  )
}
