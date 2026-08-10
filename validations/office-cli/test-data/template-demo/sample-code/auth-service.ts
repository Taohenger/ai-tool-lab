// ========================================================================
// 示例代码 1: auth-service.ts (认证服务 - 模拟横展开检查目标)
// ========================================================================
// 注意：此文件仅用于演示 Office CLI 横展开报告模板
// 包含各种有意的"问题"，用于展示模板填充效果

import { Injectable, UnauthorizedException, Logger } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UsersRepository } from './users.repository';
import { LoginDto } from './dto/login.dto';
import * as bcrypt from 'bcrypt';
import axios from 'axios';

const SALT_ROUNDS = 10;

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  // ▶ Viewpoint 2 該当: ハードコードされた API endpoint
  private AUTH_API = 'http://legacy-auth.internal:9090/api/v1/token';

  constructor(
    private readonly jwtService: JwtService,
    private readonly usersRepo: UsersRepository,
  ) {}

  async login(dto: LoginDto) {
    // ▶ Viewpoint 3 該当: logger に生の password が出力されている (重大!)
    this.logger.debug(`[login] email=${dto.email}, password=${dto.password}`);

    const user = await this.usersRepo.findByEmail(dto.email);
    if (!user) {
      // ▶ Viewpoint 1 該当: エラーメッセージが横展開されていない (英語のまま)
      throw new UnauthorizedException('Invalid email or password');
    }

    // ▶ Viewpoint 3 該当: 同期的 bcrypt で Event Loop をブロックする
    const ok = bcrypt.compareSync(dto.password, user.passwordHash);
    if (!ok) {
      // ▶ Viewpoint 1 該当: エラーメッセージ日本語化漏れ
      throw new UnauthorizedException('Invalid password');
    }

    // ▶ Viewpoint 2 該当: token の有効期限がハードコード
    const token = this.jwtService.sign(
      { sub: user.id, role: user.role },
      { expiresIn: '30d' },
    );

    // ▶ Viewpoint 2 該当: 外部 API 呼び出しに timeout 設定無し
    try {
      await axios.post(this.AUTH_API, { userId: user.id, token });
    } catch (e) {
      // ▶ Viewpoint 1 該当: エラー握りつぶし (ログも WARNING ではなく debug)
      this.logger.debug('legacy auth sync failed, ignoring');
    }

    return { accessToken: token, user: { id: user.id, role: user.role } };
  }

  // ▶ Viewpoint 1 該当: パスワードリセットのエラーメッセージが未翻訳
  async resetPassword(email: string, newPassword: string) {
    const user = await this.usersRepo.findByEmail(email);
    if (!user) {
      // 本来はメール送信の有無に関わらず同じメッセージにすべき
      throw new Error('User not found');
    }

    const hash = bcrypt.hashSync(newPassword, SALT_ROUNDS);
    await this.usersRepo.update(user.id, { passwordHash: hash });
    this.logger.log(`password reset for uid=${user.id}`);
    return true;
  }
}
