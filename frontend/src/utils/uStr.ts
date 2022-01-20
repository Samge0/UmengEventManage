
export class uStr {

  /**
   * 是否内容为空
   * @param v
   */
  static isEmpty = (v: string): boolean => {
      return !v || Object.keys(v).length === 0
  }
}