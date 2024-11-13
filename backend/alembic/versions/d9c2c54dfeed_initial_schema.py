"""Initial database migration

Revision ID: your_revision_id
Revises: 
Create Date: 2024-01-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY


# revision identifiers, used by Alembic.
revision = 'your_revision_id'  # оставьте как есть, alembic сам заполнил это значение
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # subscription_plans
    op.create_table(
        'subscription_plans',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('chat_requests_daily', sa.Integer(), nullable=False),
        sa.Column('image_generations_monthly', sa.Integer(), nullable=False),
        sa.Column('tool_cards_monthly', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # users
    op.create_table(
        'users',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100)),
        sa.Column('avatar_url', sa.String(255)),
        sa.Column('about_me', sa.Text()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('is_admin', sa.Boolean(), server_default='false'),
        sa.Column('reset_password_token', sa.String(255)),
        sa.Column('reset_password_expires', sa.TIMESTAMP(timezone=True)),
        sa.Column('email_verified_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # user_subscriptions
    op.create_table(
        'user_subscriptions',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('plan_id', UUID(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('current_period_start', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('cancel_at_period_end', sa.Boolean(), server_default='false'),
        sa.Column('payment_provider', sa.String(50)),
        sa.Column('payment_provider_subscription_id', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'])
    )

    # payments
    op.create_table(
        'payments',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', UUID()),
        sa.Column('subscription_id', UUID()),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='RUB'),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('payment_provider', sa.String(50), nullable=False),
        sa.Column('payment_provider_payment_id', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['subscription_id'], ['user_subscriptions.id'])
    )

    # chat_folders
    op.create_table(
        'chat_folders',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('emoji', sa.String(10)),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # chats
    op.create_table(
        'chats',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('folder_id', UUID()),
        sa.Column('title', sa.String(255)),
        sa.Column('auto_title_number', sa.Integer()),
        sa.Column('tags', ARRAY(sa.String())),
        sa.Column('bot_style', sa.String(50)),
        sa.Column('is_memory_enabled', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['folder_id'], ['chat_folders.id'], ondelete='SET NULL')
    )

    # chat_messages
    op.create_table(
        'chat_messages',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('chat_id', UUID(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tokens_used', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE')
    )

    # tool_usage
    op.create_table(
        'tool_usage',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('tool_type', sa.String(50), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('result', sa.Text()),
        sa.Column('tokens_used', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # api_usage
    op.create_table(
        'api_usage',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', UUID()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('endpoint', sa.String(255), nullable=False),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('tokens_used', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # blog_posts
    op.create_table(
        'blog_posts',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('meta_description', sa.String(255)),
        sa.Column('meta_keywords', sa.String(255)),
        sa.Column('is_published', sa.Boolean(), server_default='false'),
        sa.Column('published_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # email_campaigns
    op.create_table(
        'email_campaigns',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('scheduled_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # email_sends
    op.create_table(
        'email_sends',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('campaign_id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('opened_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['campaign_id'], ['email_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Создаем индексы
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_chat_messages_chat_id', 'chat_messages', ['chat_id'])
    op.create_index('idx_chat_messages_created_at', 'chat_messages', ['created_at'])
    op.create_index('idx_chats_user_id', 'chats', ['user_id'])
    op.create_index('idx_chats_folder_id', 'chats', ['folder_id'])
    op.create_index('idx_api_usage_user_id_created_at', 'api_usage', ['user_id', 'created_at'])
    op.create_index('idx_api_usage_ip_address_created_at', 'api_usage', ['ip_address', 'created_at'])
    op.create_index('idx_tool_usage_user_id_created_at', 'tool_usage', ['user_id', 'created_at'])
    op.create_index('idx_blog_posts_slug', 'blog_posts', ['slug'])
    op.create_index('idx_user_subscriptions_user_id', 'user_subscriptions', ['user_id'])
    op.create_index('idx_user_subscriptions_status', 'user_subscriptions', ['status'])


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_table('email_sends')
    op.drop_table('email_campaigns')
    op.drop_table('blog_posts')
    op.drop_table('api_usage')
    op.drop_table('tool_usage')
    op.drop_table('chat_messages')
    op.drop_table('chats')
    op.drop_table('chat_folders')
    op.drop_table('payments')
    op.drop_table('user_subscriptions')
    op.drop_table('users')
    op.drop_table('subscription_plans')
