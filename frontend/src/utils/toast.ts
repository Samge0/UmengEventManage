// toast.ts
import {ElMessage} from "element-plus";

export class toast {

  /**
   * 显示错误信息
   * @param msg
   */
  static showError = (msg: string) => {
      ElMessage({
          showClose: true,
          message: msg,
          type: 'error',
      })
  }

  /**
   * 显示成功信息
   * @param msg
   */
  static showSuccess = (msg: string) => {
      ElMessage({
          showClose: true,
          message: msg,
          type: 'success',
      })
  }

  /**
   * 显示warning信息
   * @param msg
   */
  static showWarning = (msg: string) => {
      ElMessage({
          showClose: true,
          message: msg,
          type: 'warning',
      })
  }

}