<?php
/**
 * test case
 */
require_once dirname(__FILE__).'/../classautoloader.php';

/**
 * test case.
 */
class WURFL_Cache_MemcacheCacheProviderTest extends PHPUnit_Framework_TestCase {
	
	public function testMultipleServerConfiguration() {
        $params=array(
            "host" => "127.0.0.1;127.0.0.2"
        );
        $this->checkDeps();
        $cache = new WURFL_Cache_MemcacheCacheProvider($params);		                
    }
    
	public function testNeverToExpireItems() {
		$params = array(WURFL_Configuration_Config::EXPIRATION => WURFL_Cache_CacheProvider::NEVER);
		$this->checkDeps();
		$cache = new WURFL_Cache_MemcacheCacheProvider($params);
		$cache->put("foo", "foo");
		sleep(2);
		$this->assertEquals("foo", $cache->get("foo"));
				
	}
	
	public function testShouldClearAllItems() {
		$this->checkDeps();
		$cache = new WURFL_Cache_MemcacheCacheProvider(array());
		$cache->put("key1", "item1");		
		$cache->put("key2", "item2");
		$cache->clear();
		$this->assertThanNoElementsAreInCache(array("key1", "key2"), $cache);
		
	}

	private function assertThanNoElementsAreInCache($keys = array(), $cache) {
		foreach ($keys as $key) {
			$this->assertNull($cache->get($key));
		}
	}
	
	private function checkDeps() {
		if (!extension_loaded('memcache')) {
			$this->markTestSkipped("PHP extension 'memcache' must be loaded and a local memcache server running to run this test.");
		}
	}
	
}
